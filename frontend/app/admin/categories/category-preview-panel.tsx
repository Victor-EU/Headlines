import type { PreviewResult } from "./page";

type Props = {
  preview: { categoryId: string; result: PreviewResult };
  onClose: () => void;
};

export function CategoryPreviewPanel({ preview, onClose }: Props) {
  return (
    <div className="border border-rule rounded p-4 space-y-3 bg-surface-alt">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-primary">Classification Preview</h3>
        <button onClick={onClose} className="text-xs text-secondary hover:text-primary">Close</button>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-secondary font-medium mb-2">Would Match ({preview.result.would_match.length})</p>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {preview.result.would_match.map((a) => (
              <div key={a.article_id} className="text-xs text-primary">
                {a.title} <span className="text-muted">({(a.confidence * 100).toFixed(0)}%)</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs text-secondary font-medium mb-2">Currently Matched ({preview.result.currently_matched.length})</p>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {preview.result.currently_matched.map((a) => (
              <div key={a.article_id} className="text-xs text-primary">
                {a.title} <span className="text-muted">({(a.confidence * 100).toFixed(0)}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
