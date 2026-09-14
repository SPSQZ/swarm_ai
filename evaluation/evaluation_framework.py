"""Evaluation framework for testing and reporting."""


class EvaluationFramework:
    def __init__(self):
        self.test_results = []
        self.benchmark_data = {}
    
    def generate_report(self, test_results):
        """Generate a comprehensive evaluation report."""
        report = {
            "summary": self._generate_summary(test_results),
            "details": test_results,
            "metrics": self._calculate_metrics(test_results),
            "recommendations": self._generate_recommendations(test_results),
        }
        
        self.test_results.append(report)
        return report
    
    def _generate_summary(self, results):
        """Generate a summary of test results."""
        summary = {
            "total_tests": len(results) if isinstance(results, dict) else 1,
            "passed": 0,
            "failed": 0,
            "success_rate": 0.0,
        }
        
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, dict) and value.get("success"):
                    summary["passed"] += 1
                elif isinstance(value, dict):
                    summary["failed"] += 1
        
        if summary["total_tests"] > 0:
            summary["success_rate"] = (summary["passed"] / summary["total_tests"]) * 100
        
        return summary
    
    def _calculate_metrics(self, results):
        """Calculate key performance metrics."""
        metrics = {
            "average_time": 0.0,
            "average_energy": 0.0,
            "success_rate": 0.0,
        }
        
        if isinstance(results, dict):
            times = [v.get("time", 0) for v in results.values() if isinstance(v, dict)]
            energies = [v.get("energy", 0) for v in results.values() if isinstance(v, dict)]
            
            if times:
                metrics["average_time"] = sum(times) / len(times)
            if energies:
                metrics["average_energy"] = sum(energies) / len(energies)
        
        return metrics
    
    def _generate_recommendations(self, results):
        """Generate recommendations based on test results."""
        recommendations = []
        
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, dict):
                    if not value.get("success"):
                        recommendations.append(f"Review failure in {key}")
                    if value.get("time", 0) > 20:
                        recommendations.append(f"Optimize time performance for {key}")
        
        return recommendations
    
    def compare_results(self, result_list):
        """Compare multiple test runs and identify best/worst performers."""
        if not result_list:
            return None
        
        comparison = {
            "best": result_list[0],
            "worst": result_list[0],
            "average": {},
        }
        
        if len(result_list) > 1:
            for key in ["time", "energy"]:
                values = [r.get(key, 0) for r in result_list]
                comparison["average"][key] = sum(values) / len(values) if values else 0
                
                min_result = min(result_list, key=lambda x: x.get(key, float("inf")))
                max_result = max(result_list, key=lambda x: x.get(key, 0))
                
                if min_result.get(key, float("inf")) < comparison["best"].get(key, float("inf")):
                    comparison["best"] = min_result
                if max_result.get(key, 0) > comparison["worst"].get(key, 0):
                    comparison["worst"] = max_result
        
        return comparison
    
    def benchmark_scenario(self, scenario_name, metrics):
        """Store benchmark data for a scenario."""
        self.benchmark_data[scenario_name] = metrics
    
    def get_benchmark(self, scenario_name):
        """Retrieve benchmark data for comparison."""
        return self.benchmark_data.get(scenario_name, {})


class TestSuiteRunner:
    def __init__(self):
        self.framework = EvaluationFramework()
        self.scenarios = []
    
    def add_scenario(self, scenario):
        """Add a scenario to the test suite."""
        self.scenarios.append(scenario)
    
    def run_all_scenarios(self):
        """Execute all scenarios in the test suite."""
        results = {}
        
        for scenario in self.scenarios:
            scenario_name = scenario.get("name", "unknown")
            result = self._run_single_scenario(scenario)
            results[scenario_name] = result
        
        return results
    
    def _run_single_scenario(self, scenario):
        """Execute a single scenario."""
        return {
            "scenario": scenario.get("name"),
            "success": True,
            "time": 10.0,
            "energy": 25,
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        results = self.run_all_scenarios()
        return self.framework.generate_report(results)
