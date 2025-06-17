from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel
from supabase import Client
from uuid import uuid4
from ..dependencies import get_supabase_client
from ..auth_middleware import UserClaims

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

@router.post("/")
async def create_template(
    request: Request,
    template: TemplateCreate,
    supabase: Client = Depends(get_supabase_client),
):
    """Crear un nuevo template dinámico"""
    try:
        # Get user claims from request state
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub  # Use the sub claim as the user ID

        # Generamos un ID único para el template
        template_id = str(uuid4())

        # Guardamos el template en la base de datos de Supabase
        result = supabase.table("templates").insert({
            "id": template_id,
            "name": template.name,
            "user_id": user_id,  # Asociamos el template con el usuario
            "fields": [field.model_dump() for field in template.fields]  # Guardamos los campos como JSON
        }).execute()

        # Check if the operation was successful by checking if data was returned
        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create template")

        return {
            "message": "Template creado exitosamente",
            "template_id": template_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_templates(
    request: Request,
    supabase: Client = Depends(get_supabase_client),
):
    """Listar todos los templates del usuario autenticado"""
    try:
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub

        # Buscar templates por user_id
        result = supabase.table("templates").select("*").eq("user_id", user_id).execute()

        # Check if the operation was successful
        if result.data is None:
            raise HTTPException(status_code=400, detail="Failed to fetch templates")

        return {"templates": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}")
async def get_template_details(
    request: Request,
    template_id: str,
    supabase: Client = Depends(get_supabase_client),
):
    """Obtener detalles de un template específico por su ID"""
    try:
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub

        # Buscar el template por ID y asegurar que pertenece al usuario autenticado
        result = supabase.table("templates").select("*").eq("id", template_id).eq("user_id", user_id).single().execute()

        # Check if template was found
        if not result.data:
            raise HTTPException(status_code=404, detail="Template no encontrado o no pertenece al usuario")

        return {
            "template_id": result.data["id"],
            "name": result.data["name"],
            "fields": result.data["fields"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    request: Request,
    template_id: str,
    force: bool = Query(False, description="Eliminar también si hay datos asociados"),
    supabase: Client = Depends(get_supabase_client),
):
    """Eliminar un template (con confirmación si hay datos asociados)"""
    try:
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub

        # Verificar si el template existe y pertenece al usuario
        result = supabase.table("templates").select("*").eq("id", template_id).eq("user_id", user_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Template no encontrado o no autorizado")

        # Verificar si hay datos asociados al template
        data_check = supabase.table("template_data").select("id").eq("template_id", template_id).limit(1).execute()
        if data_check.data and not force:
            raise HTTPException(
                status_code=400,
                detail="Este template tiene datos asociados. Usa 'force=true' para eliminarlo junto con los datos."
            )

        # Eliminar datos asociados (si existen y se confirma con `force`)
        if data_check.data and force:
            delete_data = supabase.table("template_data").delete().eq("template_id", template_id).execute()
            if not delete_data.data:
                raise HTTPException(status_code=500, detail="Error al eliminar los datos asociados")

        # Eliminar el template
        delete_template = supabase.table("templates").delete().eq("id", template_id).execute()
        if not delete_template.data:
            raise HTTPException(status_code=500, detail="Error al eliminar el template")

        return {"message": "Template eliminado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))