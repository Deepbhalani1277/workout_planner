/**
 * OnboardingPage.jsx — 7-step wizard to collect user profile data.
 *
 * Collects age, gender, height, weight, goal, activity level, equipment,
 * diet type, allergies, and budget.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import useUserStore from "../store/userStore";
import userService from "../services/userService";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import ErrorMessage from "../components/common/ErrorMessage";
import ProgressBar from "../components/onboarding/ProgressBar";

const EQUIPMENT_OPTIONS = [
  "No Equipment",
  "Dumbbells",
  "Resistance Bands",
  "Full Gym",
  "Home Gym",
];

export default function OnboardingPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const setIsOnboarded = useUserStore((s) => s.setIsOnboarded);

  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    age: "",
    gender: "",
    height_cm: "",
    weight_kg: "",
    fitness_goal: "",
    activity_level: "",
    equipment: [],
    diet_type: "",
    allergies: "",
    budget_range: "",
  });

  const updateForm = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    setError("");
  };

  const toggleEquipment = (eq) => {
    setFormData((prev) => {
      const eqList = prev.equipment;
      if (eqList.includes(eq)) {
        return { ...prev, equipment: eqList.filter((i) => i !== eq) };
      }
      return { ...prev, equipment: [...eqList, eq] };
    });
    setError("");
  };

  const nextStep = () => {
    setError("");
    // Validation
    if (step === 1) {
      if (!formData.age || formData.age < 13 || formData.age > 80) {
        return setError("Please enter a valid age between 13 and 80.");
      }
      if (!formData.gender) {
        return setError("Please select your gender.");
      }
    }
    if (step === 2) {
      if (!formData.height_cm || formData.height_cm < 100 || formData.height_cm > 250) {
        return setError("Please enter a valid height between 100cm and 250cm.");
      }
      if (!formData.weight_kg || formData.weight_kg < 30 || formData.weight_kg > 300) {
        return setError("Please enter a valid weight between 30kg and 300kg.");
      }
    }
    if (step === 3 && !formData.fitness_goal) {
      return setError("Please select a fitness goal.");
    }
    if (step === 4 && !formData.activity_level) {
      return setError("Please select your activity level.");
    }
    if (step === 5 && formData.equipment.length === 0) {
      return setError("Please select at least one equipment option.");
    }
    if (step === 6) {
      if (!formData.diet_type) return setError("Please select a diet type.");
      if (!formData.budget_range) return setError("Please select a budget range.");
    }

    setStep((s) => s + 1);
  };

  const prevStep = () => setStep((s) => s - 1);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError("");
    try {
      await userService.saveOnboarding({
        ...formData,
        age: parseInt(formData.age, 10),
        height_cm: parseFloat(formData.height_cm),
        weight_kg: parseFloat(formData.weight_kg),
      });
      setIsOnboarded(true);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save profile. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // ── Render Helpers ─────────────────────────────────────────────────────────

  const renderCard = (title, description, isSelected, onClick, className = "") => (
    <div
      onClick={onClick}
      className={`border-2 p-4 rounded-xl cursor-pointer transition-all duration-200 ${
        isSelected
          ? "border-primary bg-primary/5 shadow-sm"
          : "border-border bg-white hover:border-primary/50 hover:bg-gray-50"
      } ${className}`}
    >
      <h4 className={`font-semibold text-base mb-1 ${isSelected ? "text-primary" : "text-text-main"}`}>
        {title}
      </h4>
      {description && <p className="text-sm text-text-muted leading-snug">{description}</p>}
    </div>
  );

  const bmi =
    formData.height_cm && formData.weight_kg
      ? (parseFloat(formData.weight_kg) / Math.pow(parseFloat(formData.height_cm) / 100, 2)).toFixed(1)
      : null;

  // ── Steps ──────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-background flex flex-col items-center py-8 px-4 lg:py-16">
      <div className="w-full max-w-2xl bg-card rounded-card shadow-card p-6 md:p-10 relative">
        <ProgressBar currentStep={step} totalSteps={7} />
        <div className="mt-8">
          {error && <div className="mb-6"><ErrorMessage message={error} /></div>}

          {/* STEP 1 */}
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Personal Information</h2>
                <p className="text-text-muted mt-1">Let's start with the basics.</p>
              </div>
              <Input
                label="Full Name"
                value={user?.full_name || ""}
                disabled
                className="opacity-70 bg-gray-50 cursor-not-allowed"
              />
              <Input
                label="Age (13 - 80)"
                type="number"
                value={formData.age}
                onChange={(e) => updateForm("age", e.target.value)}
                placeholder="e.g. 25"
                min="13"
                max="80"
              />
              <div>
                <label className="text-sm font-medium text-text-main mb-2 block">Gender</label>
                <div className="grid grid-cols-3 gap-3">
                  {renderCard("Male", null, formData.gender === "male", () => updateForm("gender", "male"), "text-center py-3")}
                  {renderCard("Female", null, formData.gender === "female", () => updateForm("gender", "female"), "text-center py-3")}
                  {renderCard("Other", null, formData.gender === "other", () => updateForm("gender", "other"), "text-center py-3")}
                </div>
              </div>
            </div>
          )}

          {/* STEP 2 */}
          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Body Metrics</h2>
                <p className="text-text-muted mt-1">We use this to calculate your BMI and daily caloric needs.</p>
              </div>
              <Input
                label="Height (cm)"
                type="number"
                value={formData.height_cm}
                onChange={(e) => updateForm("height_cm", e.target.value)}
                placeholder="e.g. 175"
                min="100"
                max="250"
              />
              <Input
                label="Weight (kg)"
                type="number"
                value={formData.weight_kg}
                onChange={(e) => updateForm("weight_kg", e.target.value)}
                placeholder="e.g. 70"
                min="30"
                max="300"
              />
              {bmi && (
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-center">
                  <span className="text-sm text-blue-600 font-medium">Your estimated BMI is</span>
                  <div className="text-2xl font-bold text-blue-700 mt-1">{bmi}</div>
                </div>
              )}
            </div>
          )}

          {/* STEP 3 */}
          {step === 3 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Fitness Goal</h2>
                <p className="text-text-muted mt-1">What are you trying to achieve?</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {renderCard("Weight Loss", "Burn fat and lean out", formData.fitness_goal === "weight_loss", () => updateForm("fitness_goal", "weight_loss"))}
                {renderCard("Muscle Gain", "Build strength and size", formData.fitness_goal === "muscle_gain", () => updateForm("fitness_goal", "muscle_gain"))}
                {renderCard("Maintain Weight", "Stay healthy and fit", formData.fitness_goal === "maintain", () => updateForm("fitness_goal", "maintain"))}
                {renderCard("Improve Stamina", "Boost endurance and cardio", formData.fitness_goal === "stamina", () => updateForm("fitness_goal", "stamina"))}
              </div>
            </div>
          )}

          {/* STEP 4 */}
          {step === 4 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Activity Level</h2>
                <p className="text-text-muted mt-1">How active is your daily lifestyle?</p>
              </div>
              <div className="grid grid-cols-1 gap-4">
                {renderCard("Sedentary", "Desk job, little to no exercise", formData.activity_level === "sedentary", () => updateForm("activity_level", "sedentary"))}
                {renderCard("Lightly Active", "Exercise 1-3 days/week", formData.activity_level === "light", () => updateForm("activity_level", "light"))}
                {renderCard("Moderately Active", "Exercise 3-5 days/week", formData.activity_level === "moderate", () => updateForm("activity_level", "moderate"))}
                {renderCard("Very Active", "Exercise 6-7 days/week", formData.activity_level === "very_active", () => updateForm("activity_level", "very_active"))}
              </div>
            </div>
          )}

          {/* STEP 5 */}
          {step === 5 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Available Equipment</h2>
                <p className="text-text-muted mt-1">Select all that apply.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {EQUIPMENT_OPTIONS.map((eq) =>
                  renderCard(eq, null, formData.equipment.includes(eq), () => toggleEquipment(eq), "py-3")
                )}
              </div>
            </div>
          )}

          {/* STEP 6 */}
          {step === 6 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Diet Preferences</h2>
                <p className="text-text-muted mt-1">Help us tailor your meal plan.</p>
              </div>
              <div>
                <label className="text-sm font-medium text-text-main mb-2 block">Diet Type</label>
                <div className="grid grid-cols-2 gap-3 mb-6">
                  {renderCard("Vegetarian", null, formData.diet_type === "vegetarian", () => updateForm("diet_type", "vegetarian"), "py-3")}
                  {renderCard("Non-Vegetarian", null, formData.diet_type === "non_vegetarian", () => updateForm("diet_type", "non_vegetarian"), "py-3")}
                  {renderCard("Vegan", null, formData.diet_type === "vegan", () => updateForm("diet_type", "vegan"), "py-3")}
                  {renderCard("Eggetarian", null, formData.diet_type === "eggetarian", () => updateForm("diet_type", "eggetarian"), "py-3")}
                </div>
              </div>
              <Input
                label="Food Allergies (Optional)"
                value={formData.allergies}
                onChange={(e) => updateForm("allergies", e.target.value)}
                placeholder="e.g. Peanuts, Gluten"
              />
              <div className="mt-6">
                <label className="text-sm font-medium text-text-main mb-2 block">Monthly Food Budget</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {renderCard("Below ₹3000", null, formData.budget_range === "below_3000", () => updateForm("budget_range", "below_3000"), "text-center py-3")}
                  {renderCard("₹3000 - 6000", null, formData.budget_range === "3000_6000", () => updateForm("budget_range", "3000_6000"), "text-center py-3")}
                  {renderCard("Above ₹6000", null, formData.budget_range === "above_6000", () => updateForm("budget_range", "above_6000"), "text-center py-3")}
                </div>
              </div>
            </div>
          )}

          {/* STEP 7 */}
          {step === 7 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h2 className="text-2xl font-bold text-text-main">Review & Submit</h2>
                <p className="text-text-muted mt-1">Please confirm your details below.</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-5 border border-border space-y-4 text-sm">
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-text-muted">Personal Info</span>
                  <span className="font-semibold text-right">{formData.age} yrs • {formData.gender}</span>
                  <button onClick={() => setStep(1)} className="text-primary hover:underline text-xs ml-2">Edit</button>
                </div>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-text-muted">Body Metrics</span>
                  <span className="font-semibold text-right">{formData.height_cm} cm • {formData.weight_kg} kg</span>
                  <button onClick={() => setStep(2)} className="text-primary hover:underline text-xs ml-2">Edit</button>
                </div>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-text-muted">Fitness Goal</span>
                  <span className="font-semibold text-right capitalize">{formData.fitness_goal.replace('_', ' ')}</span>
                  <button onClick={() => setStep(3)} className="text-primary hover:underline text-xs ml-2">Edit</button>
                </div>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-text-muted">Activity Level</span>
                  <span className="font-semibold text-right capitalize">{formData.activity_level.replace('_', ' ')}</span>
                  <button onClick={() => setStep(4)} className="text-primary hover:underline text-xs ml-2">Edit</button>
                </div>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-text-muted">Equipment</span>
                  <span className="font-semibold text-right">{formData.equipment.join(", ")}</span>
                  <button onClick={() => setStep(5)} className="text-primary hover:underline text-xs ml-2">Edit</button>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-muted">Diet & Budget</span>
                  <span className="font-semibold text-right capitalize">{formData.diet_type.replace('_', ' ')} • {formData.budget_range.replace('_', '-')}</span>
                  <button onClick={() => setStep(6)} className="text-primary hover:underline text-xs ml-2">Edit</button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Navigation Buttons ────────────────────────────────────────── */}
        <div className="mt-10 flex items-center justify-between border-t border-border/50 pt-6">
          <Button
            variant="secondary"
            onClick={prevStep}
            disabled={step === 1 || isLoading}
            className={step === 1 ? "invisible" : ""}
          >
            Back
          </Button>
          
          {step < 7 ? (
            <Button variant="primary" onClick={nextStep}>
              Next Step
            </Button>
          ) : (
            <Button variant="primary" onClick={handleSubmit} isLoading={isLoading}>
              Complete Profile
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
