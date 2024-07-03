import pulp

# Define the number of time periods (e.g., 24 hours)
time_periods = 24

# Create a list of time periods
time = range(time_periods)

# Define generation from PV and wind (example data in kWh)
pv_generation = [5, 6, 5, 6, 8, 10, 12, 14, 15, 16, 18, 17, 16, 15, 14, 12, 10, 8, 6, 5, 4, 3, 2, 1]
wind_generation = [3, 4, 3, 4, 5, 6, 7, 8, 9, 8, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8, 7, 6]

# Define load demand (example data in kWh)
load_demand = [4, 5, 6, 7, 8, 9, 10, 12, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3]

# Define battery parameters
battery_capacity = 50  # Maximum capacity in kWh
battery_charge_efficiency = 0.95
battery_discharge_efficiency = 0.95
battery_initial_soc = 25  # Initial state of charge in kWh

# Define the optimization problem
prob = pulp.LpProblem("Energy_Management_of_Microgrid", pulp.LpMinimize)

# Decision variables
battery_charge = pulp.LpVariable.dicts("Battery_Charge", time, 0, battery_capacity)
battery_discharge = pulp.LpVariable.dicts("Battery_Discharge", time, 0, battery_capacity)
battery_soc = pulp.LpVariable.dicts("Battery_SOC", time, 0, battery_capacity)

# Objective function: Minimize the total cost (example: assume cost is proportional to load demand)
total_cost = pulp.lpSum(load_demand[t] for t in time)
prob += total_cost

# Constraints
for t in time:
    if t == 0:
        prob += battery_soc[t] == battery_initial_soc + battery_charge[t] * battery_charge_efficiency - battery_discharge[t] / battery_discharge_efficiency
    else:
        prob += battery_soc[t] == battery_soc[t-1] + battery_charge[t] * battery_charge_efficiency - battery_discharge[t] / battery_discharge_efficiency
    
    prob += pv_generation[t] + wind_generation[t] + battery_discharge[t] == load_demand[t] + battery_charge[t]
    prob += battery_soc[t] <= battery_capacity
    prob += battery_soc[t] >= 0

# Solve the problem
prob.solve()

# Print the results
print("Status:", pulp.LpStatus[prob.status])
for t in time:
    print(f"Time {t}: Battery Charge = {pulp.value(battery_charge[t]):.2f} kWh, Battery Discharge = {pulp.value(battery_discharge[t]):.2f} kWh, Battery SOC = {pulp.value(battery_soc[t]):.2f} kWh")
