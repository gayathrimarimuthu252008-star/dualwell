import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  Droplet,
  Utensils,
  Plus,
  Clock,
  Sparkles,
  Flame,
  PieChart as PieIcon,
  CheckCircle,
  Apple
} from 'lucide-react';

export const NutritionHydrationPage: React.FC = () => {
  const [hydrationData, setHydrationData] = useState<any>(null);
  const [meals, setMeals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMealModal, setShowMealModal] = useState(false);

  // Meal form state
  const [mealType, setMealType] = useState('Lunch');
  const [description, setDescription] = useState('');
  const [portionSize, setPortionSize] = useState('Medium');
  const [calories, setCalories] = useState<number | ''>(550);
  const [protein, setProtein] = useState<number | ''>(35);
  const [carbs, setCarbs] = useState<number | ''>(65);
  const [fat, setFat] = useState<number | ''>(15);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [hydRes, mealRes] = await Promise.all([
        apiClient.get('/lifestyle/hydration'),
        apiClient.get('/lifestyle/meals')
      ]);
      setHydrationData(hydRes.data);
      setMeals(mealRes.data || []);
    } catch (err) {
      console.error('Failed to load nutrition data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddWater = async (amount: number) => {
    try {
      const res = await apiClient.post('/lifestyle/hydration/quick-add', { amount_ml: amount });
      setHydrationData(res.data);
    } catch (err) {
      console.error('Hydration quick add failed:', err);
    }
  };

  const handleLogMeal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/lifestyle/meals', {
        meal_type: mealType,
        description,
        portion_size: portionSize,
        calories: calories ? Number(calories) : null,
        protein_g: protein ? Number(protein) : null,
        carbs_g: carbs ? Number(carbs) : null,
        fat_g: fat ? Number(fat) : null,
      });

      setShowMealModal(false);
      setDescription('');
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to log meal.');
    }
  };

  const totalCalories = meals.reduce((acc, m) => acc + (m.calories || 0), 0);
  const totalProtein = meals.reduce((acc, m) => acc + (m.protein_g || 0), 0);
  const totalCarbs = meals.reduce((acc, m) => acc + (m.carbs_g || 0), 0);
  const totalFat = meals.reduce((acc, m) => acc + (m.fat_g || 0), 0);

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Nutrition & Daily Hydration
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            Fuel cognitive focus for heavy study blocks and sustain muscular energy for physical training.
          </p>
        </div>

        <button
          onClick={() => setShowMealModal(true)}
          className="flex items-center space-x-1.5 bg-primary hover:bg-primary-hover text-white px-3.5 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Log Meal / Snack</span>
        </button>
      </div>

      {/* Hydration Main Card */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex-1 space-y-3 w-full">
            <div className="flex items-center space-x-2">
              <span className="p-2 rounded-xl bg-sky-50 text-sky-500">
                <Droplet className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-base font-bold text-dualtext-primary">
                  Daily Hydration Goal
                </h3>
                <p className="text-xs text-dualtext-secondary">
                  Target calibrated for cognitive alertness and muscle hydration.
                </p>
              </div>
            </div>

            <div className="flex items-baseline space-x-2">
              <span className="text-3xl sm:text-4xl font-extrabold text-dualtext-primary">
                {hydrationData?.total_consumed_ml || 0}
              </span>
              <span className="text-sm font-semibold text-dualtext-secondary">
                / {hydrationData?.goal_ml || 2500} mL ({hydrationData?.percentage || 0}%)
              </span>
            </div>

            <div className="w-full bg-dualbg rounded-full h-3 overflow-hidden">
              <div
                className="bg-sky-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, hydrationData?.percentage || 0)}%` }}
              />
            </div>

            <p className="text-xs text-dualtext-secondary italic">
              💡 {hydrationData?.smart_tip || 'Keep water on your desk during study sessions.'}
            </p>
          </div>

          {/* Quick-Add Buttons */}
          <div className="flex flex-row md:flex-col gap-2 shrink-0 w-full md:w-auto">
            <button
              onClick={() => handleAddWater(250)}
              className="flex-1 md:flex-initial flex items-center justify-center space-x-2 bg-sky-50 hover:bg-sky-100 text-sky-600 border border-sky-200 px-4 py-2.5 rounded-xl text-xs font-bold transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>+250 mL Glass</span>
            </button>
            <button
              onClick={() => handleAddWater(500)}
              className="flex-1 md:flex-initial flex items-center justify-center space-x-2 bg-sky-50 hover:bg-sky-100 text-sky-600 border border-sky-200 px-4 py-2.5 rounded-xl text-xs font-bold transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>+500 mL Bottle</span>
            </button>
          </div>
        </div>

        {/* Recent Hydration Log Strip */}
        {hydrationData?.recent_logs?.length > 0 && (
          <div className="mt-5 pt-4 border-t border-bordercolor flex items-center space-x-2 overflow-x-auto text-xs text-dualtext-secondary">
            <span className="font-semibold text-[11px] text-dualtext-primary shrink-0">Today's Intake:</span>
            {hydrationData.recent_logs.slice(0, 6).map((log: any) => (
              <span
                key={log.id}
                className="bg-dualbg px-2.5 py-1 rounded-lg shrink-0 border border-bordercolor"
              >
                +{log.amount_ml} mL at {new Date(log.logged_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Macronutrient Overview Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-4 rounded-xl border border-bordercolor shadow-xs">
          <span className="text-[10px] font-bold text-dualtext-secondary uppercase">Estimated Calories</span>
          <p className="text-xl font-extrabold text-dualtext-primary mt-1">{totalCalories} <span className="text-xs font-normal">kcal</span></p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-bordercolor shadow-xs">
          <span className="text-[10px] font-bold text-dualtext-secondary uppercase">Protein</span>
          <p className="text-xl font-extrabold text-primary mt-1">{totalProtein.toFixed(0)} <span className="text-xs font-normal">g</span></p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-bordercolor shadow-xs">
          <span className="text-[10px] font-bold text-dualtext-secondary uppercase">Carbohydrates</span>
          <p className="text-xl font-extrabold text-risk-yellow mt-1">{totalCarbs.toFixed(0)} <span className="text-xs font-normal">g</span></p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-bordercolor shadow-xs">
          <span className="text-[10px] font-bold text-dualtext-secondary uppercase">Fats</span>
          <p className="text-xl font-extrabold text-indigo-500 mt-1">{totalFat.toFixed(0)} <span className="text-xs font-normal">g</span></p>
        </div>
      </div>

      {/* Meals Log Feed */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Utensils className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-dualtext-primary">
              Today's Meals & Nutrition Logs
            </h3>
          </div>
          <span className="text-xs text-dualtext-secondary">{meals.length} meals logged</span>
        </div>

        {meals.length === 0 ? (
          <div className="p-8 text-center text-xs text-dualtext-secondary">
            No meals logged for today yet. Track your breakfast, lunch, or post-workout fuel!
          </div>
        ) : (
          <div className="space-y-3">
            {meals.map((meal) => (
              <div
                key={meal.id}
                className="p-4 rounded-xl border border-bordercolor hover:border-primary/40 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white"
              >
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-dualbg text-dualtext-primary border border-bordercolor uppercase">
                      {meal.meal_type}
                    </span>
                    <span className="text-xs text-dualtext-secondary flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(meal.logged_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </span>
                    <span className="text-xs text-dualtext-secondary">• Portion: {meal.portion_size}</span>
                  </div>
                  <h4 className="text-sm font-bold text-dualtext-primary">
                    {meal.description}
                  </h4>
                </div>

                <div className="flex items-center space-x-3 text-xs self-start sm:self-auto bg-dualbg/60 px-3 py-1.5 rounded-lg border border-bordercolor">
                  {meal.calories && (
                    <span className="font-semibold text-dualtext-primary">
                      {meal.calories} kcal
                    </span>
                  )}
                  {meal.protein_g && (
                    <span className="text-primary font-semibold">
                      P: {meal.protein_g}g
                    </span>
                  )}
                  {meal.carbs_g && (
                    <span className="text-risk-yellow font-semibold">
                      C: {meal.carbs_g}g
                    </span>
                  )}
                  {meal.fat_g && (
                    <span className="text-indigo-500 font-semibold">
                      F: {meal.fat_g}g
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Log Meal Modal */}
      {showMealModal && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 border border-bordercolor shadow-xl">
            <div className="flex items-center justify-between mb-4 border-b border-bordercolor pb-3">
              <h3 className="text-base font-bold text-dualtext-primary">
                Log Fuel & Nutrition
              </h3>
              <button
                onClick={() => setShowMealModal(false)}
                className="text-dualtext-secondary hover:text-dualtext-primary text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleLogMeal} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Meal Timing / Type
                  </label>
                  <select
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value)}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
                  >
                    <option value="Breakfast">Breakfast</option>
                    <option value="Lunch">Lunch</option>
                    <option value="Dinner">Dinner</option>
                    <option value="Snack">Snack</option>
                    <option value="Pre-workout">Pre-workout</option>
                    <option value="Post-workout">Post-workout</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Portion Size
                  </label>
                  <select
                    value={portionSize}
                    onChange={(e) => setPortionSize(e.target.value)}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
                  >
                    <option value="Small">Small</option>
                    <option value="Medium">Medium</option>
                    <option value="Large">Large</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-dualtext-primary mb-1">
                  Food Description *
                </label>
                <input
                  type="text"
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. Salmon fillet with brown rice and steamed broccoli"
                  className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-4 gap-2">
                <div>
                  <label className="block text-[11px] font-medium text-dualtext-primary mb-1">Calories</label>
                  <input
                    type="number"
                    value={calories}
                    onChange={(e) => setCalories(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-2.5 py-1.5 border border-bordercolor rounded-xl text-xs focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-dualtext-primary mb-1">Protein (g)</label>
                  <input
                    type="number"
                    value={protein}
                    onChange={(e) => setProtein(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-2.5 py-1.5 border border-bordercolor rounded-xl text-xs focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-dualtext-primary mb-1">Carbs (g)</label>
                  <input
                    type="number"
                    value={carbs}
                    onChange={(e) => setCarbs(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-2.5 py-1.5 border border-bordercolor rounded-xl text-xs focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-dualtext-primary mb-1">Fat (g)</label>
                  <input
                    type="number"
                    value={fat}
                    onChange={(e) => setFat(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-2.5 py-1.5 border border-bordercolor rounded-xl text-xs focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="flex space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowMealModal(false)}
                  className="flex-1 py-2 border border-bordercolor text-dualtext-secondary text-xs font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-xl shadow-xs"
                >
                  Save Meal Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
