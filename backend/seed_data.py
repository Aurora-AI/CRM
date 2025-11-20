import csv
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models
import auth

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

def parse_date(date_str, year_str):
    if not date_str or date_str.strip() == "":
        return datetime.utcnow()
    
    date_str = date_str.strip()
    
    # Handle "01/set" format
    months = {
        "jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06",
        "jul": "07", "ago": "08", "set": "09", "out": "10", "nov": "11", "dez": "12"
    }
    
    try:
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 2:
                day = parts[0]
                month_part = parts[1].lower()
                if month_part in months:
                    month = months[month_part]
                else:
                    month = month_part # Assume it's a number
                
                year = year_str if year_str else datetime.now().year
                return datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y")
            elif len(parts) == 3:
                # Assume DD/MM/YYYY
                return datetime.strptime(date_str, "%d/%m/%Y")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return datetime.utcnow()
    
    return datetime.utcnow()

def normalize_status(status_raw):
    if not status_raw:
        return "Qualificação"
    
    s = status_raw.strip().lower()
    if "prospecção" in s or "prospeccao" in s:
        return "Prospecção"
    if "negociação" in s or "negociacao" in s:
        return "Negociação"
    if "proposta" in s:
        return "Proposta"
    if "fechado" in s or "implantado" in s or "finalizado" in s:
        return "Fechado" # Or keep it as is if we want to see "Implantado"
    
    # Return capitalized original if no match, or default
    return status_raw.capitalize()

def seed():
    db = SessionLocal()
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "import_base.csv")
    
    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}")
        return

    print("Seeding data...")
    
    # Create a default user for unassigned or generic owners if needed
    # But the requirement says "GN (Gerente) -> Crie um usuário fictício"
    
    users_cache = {}

    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile: # utf-8-sig to handle BOM
        reader = csv.DictReader(csvfile, delimiter=';')
        
        for row in reader:
            # "CNPJ";"Ano";"GN";"Lead ou Prospecção Pura";"Produto";"CNPJ";"Fantasia";...
            # Note: CNPJ appears twice in header in the snippet? 
            # 1: CNPJ;Ano;GN;Lead ou Prospecção Pura;Produto;CNPJ;Fantasia;...
            # Python DictReader handles duplicate keys by appending suffix or we access by index?
            # DictReader might overwrite. Let's check keys.
            # If keys are duplicate, the last one wins usually.
            # Let's look at the snippet: "CNPJ;Ano;GN;...;Produto;CNPJ;Fantasia"
            # The second CNPJ is likely the one we want or they are same.
            
            gn_name = row.get("GN", "Admin").strip()
            if not gn_name:
                gn_name = "Admin"
                
            # Create User if not exists
            if gn_name not in users_cache:
                email = f"{gn_name.lower().replace(' ', '.')}@coopercard.com.br"
                user = db.query(models.User).filter(models.User.email == email).first()
                if not user:
                    # Create with dummy password (truncated to 72 bytes for bcrypt)
                    pwd = auth.get_password_hash("123456"[:72])
                    user = models.User(email=email, name=gn_name, password_hash=pwd)
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                users_cache[gn_name] = user
            
            owner = users_cache[gn_name]
            
            cnpj = row.get("CNPJ") # If duplicate, DictReader might give the last one.
            # If the CSV has duplicate headers, DictReader behavior depends on python version but usually last one.
            # Let's assume it works or use index if needed.
            
            razao_social = row.get("Fantasia")
            status_raw = row.get("Status Negociação")
            produto = row.get("Produto")
            data_contato_raw = row.get("Data Último Contato")
            ano = row.get("Ano")
            
            status = normalize_status(status_raw)
            last_interaction = parse_date(data_contato_raw, ano)
            
            # Check if opportunity exists
            opp = db.query(models.Opportunity).filter(models.Opportunity.cnpj == cnpj).first()
            if not opp:
                opp = models.Opportunity(
                    cnpj=cnpj,
                    razao_social=razao_social,
                    owner_id=owner.id,
                    status=status,
                    temperatura="Morno", # Default, or map if column exists? CSV has "Status da Oportunidade" which has "Morno", "Frio".
                    # Wait, snippet shows col "Status da Oportunidade" with values "Implantado", "Fechado".
                    # And col "Status Negociação" with "Finalizado", "Qualificação".
                    # And there is a col... wait.
                    # Line 17: ...;Negociação;Morno;...
                    # So there is a temperature column?
                    # Header: ...;Status Negociação;Status da Oportunidade;...
                    # Let's look at line 17 values vs header.
                    # 17: ...;Negociação;Morno;...
                    # Header index check:
                    # ...;Data Último Contato;Status Negociação;Status da Oportunidade;...
                    # So "Status da Oportunidade" seems to contain Temperature values like "Morno", "Frio" in some rows?
                    # Line 2: "Implantado" in "Status da Oportunidade".
                    # Line 17: "Morno" in "Status da Oportunidade".
                    # Prompt says: "Temperatura: ['Frio', 'Morno', 'Quente', 'Fervendo']"
                    # I will try to map "Status da Oportunidade" to Temperatura if it matches, otherwise default to "Frio".
                    
                    produto=produto,
                    valor_estimado=0.0, # Need to parse "FATURAMENTO PRESUMIDO ANUAL" or similar? Prompt says "valor_estimado".
                    # CSV has "FATURAMENTO PRESUMIDO ANUAL" (R$ 69.000,00).
                    # I'll try to parse it.
                    last_interaction_date=last_interaction
                )
                
                # Parse Temperature
                temp_raw = row.get("Status da Oportunidade")
                if temp_raw and temp_raw in ["Frio", "Morno", "Quente", "Fervendo"]:
                    opp.temperatura = temp_raw
                else:
                    opp.temperatura = "Frio" # Default
                
                # Parse Value
                faturamento = row.get("FATURAMENTO PRESUMIDO ANUAL")
                if faturamento:
                    try:
                        # R$ 69.000,00 -> 69000.00
                        val = faturamento.replace("R$", "").replace(".", "").replace(",", ".").strip()
                        opp.valor_estimado = float(val)
                    except:
                        pass
                
                db.add(opp)
        
        db.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    seed()
