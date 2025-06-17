from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field as PydanticField
from typing import Any, Dict
from supabase import Client
from uuid import uuid4
from datetime import datetime
from ..dependencies import get_supabase_client
from ..auth_middleware import UserClaims

router = APIRouter()

class TemplateDataCreate(BaseModel):
    values: Dict[str, Any] = PydanticField(
        ...,
        description="Dictionary of field values where keys match template field names"
    )

def validate_field_value(field_type: str, value: Any) -> bool:
    """Validate that a value matches its expected type"""
    try:
        if field_type == "string":
            return isinstance(value, str)
        elif field_type == "int":
            # Allow both strings that can be converted to int and actual ints
            if isinstance(value, str):
                int(value)
            return isinstance(value, (int, str))
        elif field_type == "float":
            # Allow both strings that can be converted to float and actual floats
            if isinstance(value, str):
                float(value)
            return isinstance(value, (float, str))
        elif field_type == "boolean":
            return isinstance(value, bool)
        elif field_type == "date":
            # Validate date string format (assuming ISO format)
            if isinstance(value, str):
                datetime.fromisoformat(value)
                return True
            return False
        else:
            return True  # For unknown types, accept any value
    except (ValueError, TypeError):
        return False

@router.post("/{template_id}/data")
async def create_template_data(
    request: Request,
    template_id: str,
    data: TemplateDataCreate,
    supabase: Client = Depends(get_supabase_client),
):
    """Create a new data entry for a template"""
    try:
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub

        # Verify template exists and belongs to user
        template_result = supabase.table("templates").select("*").eq("id", template_id).eq("user_id", user_id).single().execute()

        if not template_result.data:
            raise HTTPException(status_code=404, detail="Template no encontrado o no autorizado")

        template = template_result.data
        template_fields = template["fields"]

        # Validate all required fields are present and have correct types
        field_errors = []
        for field in template_fields:
            field_name = field["name"]
            field_type = field["type"]

            # Check if field value exists
            if field_name not in data.values:
                continue  # Skip validation if field is not provided (no fields are required)

            # Validate field type
            if not validate_field_value(field_type, data.values[field_name]):
                field_errors.append(f"El valor para el campo '{field_name}' no es del tipo esperado: {field_type}")

        if field_errors:
            raise HTTPException(
                status_code=400,
                detail={"message": "Error de validación", "errors": field_errors}
            )

        # Create the data entry
        result = supabase.table("template_data").insert({
            "template_id": template_id,
            "user_id": user_id,
            "values": data.values
        }).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Error al crear el registro de datos")

        return {
            "message": "Datos guardados exitosamente",
            "data_id": result.data[0]["id"]
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}/data")
async def list_template_data(
    request: Request,
    template_id: str,
    supabase: Client = Depends(get_supabase_client),
):
    """List all data entries for a specific template"""
    try:
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub

        # Verify template exists and belongs to user
        template_exists = supabase.table("templates").select("id").eq("id", template_id).eq("user_id", user_id).single().execute()

        if not template_exists.data:
            raise HTTPException(status_code=404, detail="Template no encontrado o no autorizado")

        # Get all data entries for this template
        result = supabase.table("template_data").select("*").eq("template_id", template_id).eq("user_id", user_id).order("created_at", desc=True).execute()

        return {"data": result.data}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}/data/{data_id}")
async def get_template_data(
    request: Request,
    template_id: str,
    data_id: str,
    supabase: Client = Depends(get_supabase_client),
):
    """Get a specific data entry for a template"""
    try:
        user_claims: UserClaims = request.state.user
        user_id = user_claims.sub

        # Get the specific data entry
        result = supabase.table("template_data").select("*").eq("id", data_id).eq("template_id", template_id).eq("user_id", user_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Registro no encontrado o no autorizado")

        return result.data

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))