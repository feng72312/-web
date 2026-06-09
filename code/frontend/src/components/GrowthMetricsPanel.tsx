import { PRICING_TIERS } from "../config/pricingTiers";
import { ResultCard } from "./ui/ResultCard";

export function GrowthMetricsPanel() {
  return (
    <ResultCard title="权益分层">
      <div className="pricing-tier-grid">
        {PRICING_TIERS.map((tier) => (
          <article key={tier.id} className="pricing-tier-card">
            <h4>{tier.label}</h4>
            <ul>
              {tier.features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </ResultCard>
  );
}
