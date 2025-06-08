from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import Client
from uuid import uuid4
from ..dependencies import get_supabase_client, get_current_user

router = APIRouter()

# Definimos el modelo para los campos del template
class Field(BaseModel):
    name: str         # Nombre del campo (e.g., "marca", "volumen")
    type: str         # Tipo de dato (string, int, etc.)
    display_unit: str | None = None  # Unidad de visualización (e.g., "ml", "km")

# Definimos el modelo para el template
class TemplateCreate(BaseModel):
    name: str         # Nombre del template (e.g., "Agua Tomada")
    fields: list[Field]  # Lista de campos definidos por el usuario

@router.post("/templates")
async def create_template(
    template: TemplateCreate,
    supabase: Client = Depends(get_supabase_client),
    current_user = Depends(get_current_user)  # Obtén el usuario autenticado
):
    """Crear un nuevo template dinámico"""
    try:
        # Generamos un ID único para el template
        template_id = str(uuid4())
        user_id = current_user.get("id")  # Obtenemos el ID del usuario autenticado
        
        # Guardamos el template en la base de datos de Supabase
        result = supabase.table("templates").insert({
            "id": template_id,
            "name": template.name,
            "user_id": user_id,  # Asociamos el template con el usuario
            "fields": [field.dict() for field in template.fields]  # Guardamos los campos como JSON
        }).execute()

        if result.error:
            raise HTTPException(status_code=400, detail=result.error.message)

        return {
            "message": "Template creado exitosamente",
            "template_id": template_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def list_templates(
    supabase: Client = Depends(get_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    """Listar todos los templates del usuario autenticado"""
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario no válido")

        # Buscar templates por user_id
        result = supabase.table("templates").select("*").eq("user_id", user_id).execute()

        if result.error:
            raise HTTPException(status_code=400, detail=result.error.message)

        return {"templates": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/templates/{template_id}")
async def get_template_details(
    template_id: str,
    supabase: Client = Depends(get_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    """Obtener detalles de un template específico por su ID"""
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Usuario no válido")

        # Buscar el template por ID y asegurar que pertenece al usuario autenticado
        result = supabase.table("templates").select("*").eq("id", template_id).eq("user_id", user_id).single().execute()

        if result.error:
            raise HTTPException(status_code=404, detail="Template no encontrado o no pertenece al usuario")

        return {
            "template_id": result.data["id"],
            "name": result.data["name"],
            "fields": result.data["fields"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))