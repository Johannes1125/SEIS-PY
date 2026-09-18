"""
ml/predictor.py - Multi-Output Ensemble Machine Learning Pipeline
"""
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from ml.dataset import generate_synthetic_dataset

class SeismicMLPredictor:
    """
    Multi-Output Machine Learning Model for instant seismic response prediction.
    """
    def __init__(self):
        self.model = None
        self.feature_names = [
            "stories", "story_height", "plan_area", "fc", "fy", "rebar_ratio",
            "pga", "zone_val", "soil_idx", "fault_dist", "frame_r", "shape_idx"
        ]
        self.target_names = ["roof_disp_mm", "max_idr_pct", "base_shear_kn", "period_s", "damage_index"]
        self.metrics = {}
        self.feature_importances = None
        
    def _encode_features(self, df: pd.DataFrame) -> np.ndarray:
        soil_map = {"SA": 0, "SB": 1, "SC": 2, "SD": 3, "SE": 4}
        zone_map = {"Zone 2": 2, "Zone 4": 4}
        r_map = {"SMRF": 8.5, "IMRF": 5.5, "OMRF": 3.5}
        shape_map = {"REGULAR": 0, "L_SHAPE": 1, "T_SHAPE": 2, "SOFT_STORY": 3}
        
        X = np.zeros((len(df), len(self.feature_names)))
        X[:, 0] = df["stories"].values
        X[:, 1] = df["story_height"].values
        X[:, 2] = df["plan_area"].values
        X[:, 3] = df["fc"].values
        X[:, 4] = df["fy"].values
        X[:, 5] = df["rebar_ratio"].values
        X[:, 6] = df["pga"].values
        X[:, 7] = df["zone"].map(lambda z: zone_map.get(z, 4)).values
        X[:, 8] = df["soil_type"].map(lambda s: soil_map.get(s, 3)).values
        X[:, 9] = df["fault_dist"].values
        X[:, 10] = df["frame_type"].map(lambda f: r_map.get(f, 8.5)).values
        X[:, 11] = df["plan_shape"].map(lambda s: shape_map.get(s, 0)).values
        return X
    
    def train(self, df: pd.DataFrame):
        X = self._encode_features(df)
        Y = df[self.target_names].values
        
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.15, random_state=42)
        
        base_rf = RandomForestRegressor(n_estimators=80, max_depth=14, n_jobs=-1, random_state=42)
        self.model = MultiOutputRegressor(base_rf)
        self.model.fit(X_train, Y_train)
        
        Y_pred = self.model.predict(X_test)
        
        for i, target in enumerate(self.target_names):
            r2 = r2_score(Y_test[:, i], Y_pred[:, i])
            rmse = math.sqrt(mean_squared_error(Y_test[:, i], Y_pred[:, i]))
            self.metrics[target] = {"r2": round(r2, 4), "rmse": round(rmse, 4)}
            
        importances = np.mean([est.feature_importances_ for est in self.model.estimators_], axis=0)
        self.feature_importances = dict(zip(self.feature_names, importances))
        
    def predict_single(self, *args, **kwargs):
        """
        Universal predictor supporting positional or keyword arguments.
        """
        if args:
            # Handle positional arguments
            stories = args[0]
            story_height = args[1]
            plan_area = args[2]
            fc = args[3]
            fy = args[4]
            rebar_ratio = args[5]
            pga = args[6]
            zone = args[7]
            soil_type = args[8]
            fault_dist = args[9]
            frame_type = args[10]
            plan_shape = args[11] if len(args) > 11 else kwargs.get("plan_shape", "REGULAR")
        else:
            stories = kwargs.get("stories", 2)
            story_height = kwargs.get("story_height", 3.0)
            plan_area = kwargs.get("plan_area", 120.0)
            fc = kwargs.get("fc", 21.0)
            fy = kwargs.get("fy", 275.0)
            rebar_ratio = kwargs.get("rebar_ratio", 1.5)
            pga = kwargs.get("pga", 0.40)
            zone = kwargs.get("zone", "Zone 4")
            soil_type = kwargs.get("soil_type", "SD")
            fault_dist = kwargs.get("fault_dist", 5.0)
            frame_type = kwargs.get("frame_type", "SMRF")
            plan_shape = kwargs.get("plan_shape", "REGULAR")

        df_single = pd.DataFrame([{
            "stories": stories,
            "story_height": story_height,
            "plan_area": plan_area,
            "fc": fc,
            "fy": fy,
            "rebar_ratio": rebar_ratio,
            "pga": pga,
            "zone": zone,
            "soil_type": soil_type,
            "fault_dist": fault_dist,
            "frame_type": frame_type,
            "plan_shape": plan_shape
        }])
        
        X = self._encode_features(df_single)
        pred = self.model.predict(X)[0]
        
        return {
            "roof_disp_mm": max(0.1, round(float(pred[0]), 2)),
            "max_idr_pct": max(0.01, round(float(pred[1]), 3)),
            "base_shear_kn": max(1.0, round(float(pred[2]), 2)),
            "period_s": max(0.05, round(float(pred[3]), 3)),
            "damage_index": max(0.01, min(1.25, round(float(pred[4]), 3)))
        }

# Global singleton loader
_GLOBAL_MODEL = None
_GLOBAL_DATASET = None

def get_trained_model(force_retrain=False):
    """Returns a trained SeismicMLPredictor singleton."""
    global _GLOBAL_MODEL, _GLOBAL_DATASET
    if _GLOBAL_MODEL is None or force_retrain:
        _GLOBAL_DATASET = generate_synthetic_dataset(n_samples=3500)
        _GLOBAL_MODEL = SeismicMLPredictor()
        _GLOBAL_MODEL.train(_GLOBAL_DATASET)
    return _GLOBAL_MODEL, _GLOBAL_DATASET
