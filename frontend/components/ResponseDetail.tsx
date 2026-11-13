import type { FeedbackResponse } from "@/lib/api";
import { categoryLabel, kindLabel, sourceLabel } from "@/lib/format";
import { SidePanel } from "./SidePanel";
import { StarsDisplay } from "./Stars";

interface ResponseDetailProps {
  response: FeedbackResponse | null; // null = nothing selected, so the panel is closed
  onClose: () => void;
}

/** Everything about one response (the drill-down opened from the table). */
export function ResponseDetail({ response, onClose }: ResponseDetailProps) {
  return (
    <SidePanel title="Response details" open={response !== null} onClose={onClose}>
      {response && (
        <>
          <p className="alert-score">
            <strong>{response.customer.name}</strong>
            <span className={`chip ${chipClass(response.category)}`}>
              {categoryLabel(response.category)}
            </span>
          </p>
          <dl className="fields">
            <div>
              <dt>Email</dt>
              <dd>{response.customer.email ?? <span className="muted">Not provided</span>}</dd>
            </div>
            <div>
              <dt>Phone</dt>
              <dd>{response.customer.phone ?? <span className="muted">Not provided</span>}</dd>
            </div>
            <div>
              <dt>Customer type</dt>
              <dd>{kindLabel(response.customer.kind)}</dd>
            </div>
            <div>
              <dt>Answered via</dt>
              <dd>{sourceLabel(response.source)}</dd>
            </div>
            <div>
              <dt>Submitted</dt>
              <dd>{new Date(response.created_at).toLocaleString()}</dd>
            </div>
          </dl>
          <dl className="fields">
            <div>
              <dt>Product</dt>
              <dd>
                <StarsDisplay value={response.product_rating} />
              </dd>
            </div>
            <div>
              <dt>Customer care</dt>
              <dd>
                <StarsDisplay value={response.care_rating} />
              </dd>
            </div>
            <div>
              <dt>Happiness</dt>
              <dd>
                <StarsDisplay value={response.happy_rating} />
              </dd>
            </div>
            <div>
              <dt>Average</dt>
              <dd>{response.mean.toFixed(2)} / 5</dd>
            </div>
          </dl>
        </>
      )}
    </SidePanel>
  );
}

/** Which colour class a verdict chip uses. */
function chipClass(category: FeedbackResponse["category"]): string {
  if (category === "detractor") return "chip-bad";
  if (category === "passive") return "chip-muted";
  return "chip-ok";
}
