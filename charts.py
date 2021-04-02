from seppecher2012 import EmploymentStatus, LoanQuality
import matplotlib
import matplotlib.pyplot as plt
from statistics import mean

def unemployment_duration(step):
    unemployed = [household for household in list(step.households.values()) if household.employment_status != EmploymentStatus.EMPLOYED]
    return sum([household.unemployment_duration for household in unemployed]) / len(unemployed)

def plot_unemployment_duration(run):
    durations = [unemployment_duration(step) for step in run]
    fig, ax = plt.subplots()
    ax.plot(range(len(durations)), durations)

    ax.set(xlabel='step', ylabel='months',
        title='Unemployment duration')
    ax.grid()

    plt.show()


def unemployment_level(step):
    unemployed = [household for household in list(step.households.values()) if household.employment_status != EmploymentStatus.EMPLOYED]
    return len(unemployed)

def vacancies_level(step):
    return sum([firm.hiring_vacancies
                for firm in step.firms.values()
                if not step.bank.accounts[firm.account_id].bankrupt])

def plot_unemployment_vacancies(run):
    unemployment = [unemployment_level(step) for step in run]
    vacancies = [vacancies_level(step) for step in run]
    fig, ax = plt.subplots()
    ax.plot(range(len(unemployment)), unemployment)
    ax.plot(range(len(vacancies)), vacancies)

    ax.set(xlabel='step', ylabel='Households / Vacancies',
        title='Unemployment / Vacancies')
    ax.grid()

    plt.show()

def production_volume(step):
    return sum([firm.production_volume for firm in step.firms.values()])

def consumption_volume(step):
    return sum([household.consumption_volume for household in step.households.values()])

def plot_production_consumption(run):
    production = [production_volume(step) for step in run]
    consumption = [consumption_volume(step) for step in run]
    fig, ax = plt.subplots()
    ax.plot(range(len(production)), production)
    ax.plot(range(len(consumption)), consumption)

    ax.set(xlabel='step', ylabel='Volume',
        title='Production / Consumption')
    ax.grid()

    plt.show()

def loan_quality_count(quality, step):
    return sum([len([loan for loan in account.loans.values()
                     if loan.quality == quality])
               for account in step.bank.accounts.values()])

def bankruptcies_count(step):
    return len([account for account in step.bank.accounts.values()
                if account.bankrupt])

def plot_bankruptcies_loan_qualities(run):
    bankruptcies = [bankruptcies_count(step) for step in run]
    good = [loan_quality_count(LoanQuality.GOOD, step) for step in run]
    doubtful = [loan_quality_count(LoanQuality.DOUBTFUL, step) for step in run]
    bad = [loan_quality_count(LoanQuality.BAD, step) for step in run]
    fig, ax = plt.subplots()
    ax.plot(range(len(bankruptcies)), bankruptcies)
    ax.plot(range(len(good)), good)
    ax.plot(range(len(doubtful)), doubtful)
    ax.plot(range(len(bad)), bad)

    ax.set(xlabel='step', ylabel='Accounts / Loans',
        title='Bankruptcies / Good Loans / Doubtful Loans / Bad Loans')
    ax.grid()

    plt.show()

def household_balance_total(step):
    return sum([step.bank.accounts[household.account_id].balance for household in step.households.values()])

def firm_balance_total(step):
    return sum([step.bank.accounts[firm.account_id].balance for firm in step.firms.values()])

def plot_balance_totals(run):
    household = [household_balance_total(step) for step in run]
    firm = [firm_balance_total(step) for step in run]
    fig, ax = plt.subplots()
    ax.plot(range(len(household)), household)
    ax.plot(range(len(firm)), firm)

    ax.set(xlabel='step', ylabel='cents',
        title='Household Balance Total / Firm Balance Total')
    ax.grid()

    plt.show()

def firm_inventory_volume_total(step):
    return sum([firm.inventory_volume for firm in step.firms.values()])

def plot_inventory_volume_totals(run):
    vol = [firm_inventory_volume_total(step) for step in run]
    fig, ax = plt.subplots()
    ax.plot(range(len(vol)), vol)

    ax.set(xlabel='step', ylabel='units',
        title='Firm Inventory Volume Total')
    ax.grid()

    plt.show()

def price(step):
    prices = [firm.inventory_for_sale_unit_price
                 for firm in step.firms.values()
                 if not step.bank.accounts[firm.account_id].bankrupt]
    if len(prices) == 0:
      return 0
    return mean(prices)

def wage(step):
    wages = [firm.hiring_wage
                 for firm in step.firms.values()
                 if not step.bank.accounts[firm.account_id].bankrupt]
    if len(wages) == 0:
      return 0
    return mean(wages)

def plot_price_wage(run):
    prices = [price(step) for step in run]
    wages = [wage(step) for step in run]

    fig, ax = plt.subplots()
    ax.plot(range(len(prices)), prices)
    ax.plot(range(len(wages)), wages)

    ax.set(xlabel='step', ylabel='cents',
        title='Mean Price / Mean Offered Wage')
    ax.grid()

    plt.show()

def plot_all(run):
  plot_unemployment_duration(run)
  plot_unemployment_vacancies(run)
  plot_production_consumption(run)
  plot_bankruptcies_loan_qualities(run)
  plot_balance_totals(run)
  plot_inventory_volume_totals(run)
  plot_price_wage(run)
