import numpy as np

def natural_language_explanation(shap_values, feature_names, feature_values):
    """
    Convert SHAP values into human-readable explanation.
    """
    # Convert to numpy array if needed
    shap_values = np.array(shap_values)
    
    # Get absolute importance ranking
    abs_values = np.abs(shap_values)
    # Get indices of top 3 most important features
    top_indices = abs_values.argsort()[::-1][:3]

    explanations = []

    for idx in top_indices:
        feature = feature_names[idx]
        value = feature_values[idx]
        shap_val = shap_values[idx]

        # Determine direction
        if shap_val > 0:
            direction = "increases risk"
            icon = "🔴"
        else:
            direction = "reduces risk"
            icon = "🔵"

        # --- CUSTOM EXPLANATIONS FOR NEW FEATURES ---
        if feature == "velocity_count":
            msg = f"{icon} High transaction frequency ({value:.0f} txns recently) {direction}"
        elif feature == "smurf_risk":
            msg = f"{icon} Pattern resembling 'Smurfing' (Structuring) {direction}"
        elif feature == "mule_risk":
            msg = f"{icon} Rapid accumulation of funds (Mule Pattern) {direction}"
        elif feature == "amount":
            msg = f"{icon} Transaction amount ({value:.2f}) {direction}"
        elif feature == "rule_risk":
            msg = f"{icon} Violation of AML rules {direction}"
        elif feature == "behavior_risk":
            msg = f"{icon} Deviation from user's normal behavior {direction}"
        elif feature == "graph_risk":
            msg = f"{icon} Connection to high-risk accounts {direction}"
        elif feature == "hour":
            msg = f"{icon} Transaction time (Hour {value}) {direction}"
        elif feature == "risky_country_flag":
            msg = f"{icon} Involvement of high-risk country {direction}"
        else:
            # Fallback for any other features
            msg = f"{icon} Feature '{feature}' {direction}"

        explanations.append(msg)

    # Join all explanations
    if not explanations:
        return "No significant risk factors detected."
        
    final_text = "**Top Risk Factors:**\n\n" + "\n".join(f"- {exp}" for exp in explanations)
    return final_text