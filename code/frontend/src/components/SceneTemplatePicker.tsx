import { SCENE_TEMPLATES } from "../config/sceneTemplates";

interface SceneTemplatePickerProps {
  activeModuleId: string;
  onSelect: (prompt: string, jumpModuleId?: string) => void;
}

export function SceneTemplatePicker({ activeModuleId, onSelect }: SceneTemplatePickerProps) {
  const templates = SCENE_TEMPLATES.filter((t) => t.moduleIds.includes(activeModuleId));
  if (templates.length === 0) {
    return null;
  }
  return (
    <div className="scene-template-picker">
      <span className="scene-template-label">场景提问</span>
      <div className="scene-template-list">
        {templates.map((item) => (
          <button
            key={item.id}
            type="button"
            className="secondary scene-template-btn"
            onClick={() =>
              onSelect(
                item.prompt,
                item.moduleIds.find((id) => id !== activeModuleId),
              )
            }
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
