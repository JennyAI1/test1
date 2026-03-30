from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import EmbeddedApp, User
from app.schemas.embedded_apps import EmbeddedAppCreate, EmbeddedAppResponse, ReorderEmbeddedAppsRequest
from app.services.embed_service import validate_embeddable_url

router = APIRouter(prefix="/embedded-apps", tags=["embedded-apps"])


@router.get("", response_model=list[EmbeddedAppResponse])
def list_embedded_apps(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    apps = (
        db.query(EmbeddedApp)
        .filter(EmbeddedApp.user_id == user.id, EmbeddedApp.is_active.is_(True))
        .order_by(EmbeddedApp.panel_order.asc(), EmbeddedApp.id.asc())
        .all()
    )
    return [
        EmbeddedAppResponse(
            id=app.id,
            title=app.title,
            url=app.url,
            category=app.category,
            panel_order=app.panel_order,
            created_at=app.created_at,
        )
        for app in apps
    ]


@router.post("", response_model=EmbeddedAppResponse)
def create_embedded_app(
    payload: EmbeddedAppCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    validate_embeddable_url(str(payload.url))

    max_order = db.query(EmbeddedApp.panel_order).filter(EmbeddedApp.user_id == user.id).order_by(EmbeddedApp.panel_order.desc()).first()
    next_order = (max_order[0] + 1) if max_order else 0

    app = EmbeddedApp(
        user_id=user.id,
        title=payload.title,
        url=str(payload.url),
        category=payload.category,
        panel_order=next_order,
        is_active=True,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    return EmbeddedAppResponse(
        id=app.id,
        title=app.title,
        url=app.url,
        category=app.category,
        panel_order=app.panel_order,
        created_at=app.created_at,
    )


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_embedded_app(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = db.query(EmbeddedApp).filter(EmbeddedApp.id == app_id, EmbeddedApp.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Embedded app not found")

    app.is_active = False
    db.commit()
    return None


@router.post("/reorder", response_model=list[EmbeddedAppResponse])
def reorder_embedded_apps(
    payload: ReorderEmbeddedAppsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    apps = (
        db.query(EmbeddedApp)
        .filter(EmbeddedApp.user_id == user.id, EmbeddedApp.is_active.is_(True))
        .all()
    )
    apps_by_id = {app.id: app for app in apps}

    if set(payload.ordered_ids) != set(apps_by_id.keys()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ordered_ids must match current app ids")

    for index, app_id in enumerate(payload.ordered_ids):
        apps_by_id[app_id].panel_order = index

    db.commit()

    ordered_apps = [apps_by_id[app_id] for app_id in payload.ordered_ids]
    return [
        EmbeddedAppResponse(
            id=app.id,
            title=app.title,
            url=app.url,
            category=app.category,
            panel_order=app.panel_order,
            created_at=app.created_at,
        )
        for app in ordered_apps
    ]
