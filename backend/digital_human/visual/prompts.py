from dataclasses import dataclass

from .domain import IdentityLock, VisualGenerationRequest, VisualIdentityProfile


@dataclass(frozen=True)
class PromptComponent:
    component_id: str
    version: str
    text: str


@dataclass(frozen=True)
class AssembledPrompt:
    text: str
    component_versions: tuple[str, ...]


class VisualPromptBuilder:
    """Assembles auditable layers rather than an uncontrolled monolithic prompt."""

    ORDER = ("IDENTITY", "SCENE", "WARDROBE", "POSE", "EXPRESSION", "CAMERA", "LIGHTING", "BRAND", "QUALITY", "NEGATIVE")

    def build(self, identity: VisualIdentityProfile, lock: IdentityLock, request: VisualGenerationRequest) -> AssembledPrompt:
        layers = {
            "IDENTITY": f"{identity.name}; {', '.join(identity.face.visible_attributes)}; {identity.eyes.color} eyes; {identity.hair.color_family} hair; references {', '.join(lock.canonical_reference_ids)}",
            "SCENE": request.scene,
            "WARDROBE": f"{request.wardrobe.category}, {request.wardrobe.color}, {request.wardrobe.fit}",
            "POSE": request.pose,
            "EXPRESSION": request.expression.value,
            "CAMERA": f"{request.camera.shot_type}, {request.camera.angle}, {request.camera.lens_equivalent}, {request.aspect_ratio}",
            "LIGHTING": request.lighting,
            "BRAND": ", ".join(identity.brand.directions),
            "QUALITY": "photorealistic natural skin, believable anatomy, clean image",
            "NEGATIVE": "do not change identity or eye color; no plastic skin, over-retouching, fantasy styling, random text, extra accessories, anatomy defects",
        }
        return AssembledPrompt("\n".join(f"[{name}] {layers[name]}" for name in self.ORDER),
                               tuple(f"visual.{name.lower()}.v1" for name in self.ORDER))
