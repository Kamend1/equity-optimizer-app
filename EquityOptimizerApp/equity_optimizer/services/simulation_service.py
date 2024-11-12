import os
import json
import numpy as np
import pandas as pd
from EquityOptimizerApp.equity_optimizer.utils import generate_portfolio_weights, simulation_engine
from django.conf import settings


class SimulationService:

    @staticmethod
    def run_simulation(stock_symbols, n, initial_investment, sim_runs, risk_free_rate, close_price_df):
        progress_file_path = os.path.join(settings.BASE_DIR, 'progress.json')
        progress = {"current": 0, "total": sim_runs}
        with open(progress_file_path, 'w') as file:
            json.dump(progress, file)

        weights_runs = np.zeros((sim_runs, n))
        sharpe_ratio_runs = np.zeros(sim_runs)
        expected_portfolio_returns_runs = np.zeros(sim_runs)
        volatility_runs = np.zeros(sim_runs)
        return_on_investment_runs = np.zeros(sim_runs)
        final_value_runs = np.zeros(sim_runs)

        print("Starting simulation...")

        for i in range(sim_runs):
            weights = generate_portfolio_weights(n)
            weights_runs[i, :] = weights

            try:
                expected_return, volatility, sharpe_ratio, final_value, roi = simulation_engine(
                    close_price_df, weights, initial_investment, risk_free_rate
                )

                sharpe_ratio_runs[i] = sharpe_ratio
                expected_portfolio_returns_runs[i] = expected_return
                volatility_runs[i] = volatility
                final_value_runs[i] = final_value
                return_on_investment_runs[i] = roi

                progress["current"] = i + 1
                with open(progress_file_path, 'w') as progress_file:
                    json.dump(progress, progress_file)
                    progress_file.flush()
                    os.fsync(progress_file.fileno())

                print(f"Run {i + 1}/{sim_runs} complete. Sharpe Ratio: {sharpe_ratio:.2f}, Final Value: ${final_value:.2f}")

            except Exception as e:
                print(f"Error during simulation run {i + 1}: {e}")

        progress["current"] = sim_runs
        with open(progress_file_path, 'w') as progress_file:
            json.dump(progress, progress_file)
            progress_file.flush()
            os.fsync(progress_file.fileno())

        print("All simulation runs completed.")

        sim_out_df = pd.DataFrame({
            'Volatility': volatility_runs.tolist(),
            'Portfolio_Return': expected_portfolio_returns_runs.tolist(),
            'Sharpe_Ratio': sharpe_ratio_runs.tolist(),
            'Final_Value': final_value_runs.tolist(),
            'Return_on_Investment': return_on_investment_runs.tolist(),
            'Weights': [weights_runs[i, :] for i in range(sim_runs)]
        })

        max_sharpe_idx = sim_out_df['Sharpe_Ratio'].idxmax()
        print(f"Best portfolio index: {max_sharpe_idx}")

        best_portfolio_data = {
            'Volatility': sim_out_df.at[max_sharpe_idx, 'Volatility'],
            'Portfolio_Return': sim_out_df.at[max_sharpe_idx, 'Portfolio_Return'],
            'Sharpe_Ratio': sim_out_df.at[max_sharpe_idx, 'Sharpe_Ratio'],
            'Final_Value': sim_out_df.at[max_sharpe_idx, 'Final_Value'],
            'Return_on_Investment': sim_out_df.at[max_sharpe_idx, 'Return_on_Investment'],
            'Weights': sim_out_df.at[max_sharpe_idx, 'Weights']
        }

        print("Simulation completed successfully. Best portfolio extracted.")

        return sim_out_df, best_portfolio_data
