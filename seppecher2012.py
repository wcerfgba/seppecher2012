import enum
from enum import Enum
from fractions import Fraction
from functools import cmp_to_key, reduce
from math import ceil, floor
from random import random, randrange, sample, shuffle
from statistics import mean
from typing import NamedTuple

class LoanQuality(Enum):
    GOOD = enum.auto()
    DOUBTFUL = enum.auto()
    BAD = enum.auto()

class Loan(NamedTuple):
    id: int
    quality: LoanQuality
    initial_value: int
    principal: int
    term: int
    time_remaining: int
    interest_rate: Fraction

class Account(NamedTuple):
    id: int
    balance: int = 0
    loans: dict[int, Loan] = {}
    loans_issued: int = 0
    bankrupt: bool = False

class Bank(NamedTuple):
    capital: int = 0
    accounts: dict[int, Account] = {}
    accounts_issued: int = 0
    accommodating: bool = True
    target_capital_ratio: Fraction = Fraction(10, 100)
    propensity_to_distribute_excess_capital: Fraction = Fraction(50, 100)
    loan_normal_interest_rate: Fraction = Fraction(5, 100)
    loan_term: int = 12
    loan_normal_rate: Fraction = Fraction(5, 100)
    loan_penalty_rate: Fraction = Fraction(10, 100)

class EmploymentStatus(Enum):
    EMPLOYED = enum.auto()
    INVOLUNTARY_UNEMPLOYED = enum.auto()
    VOLUNTARY_UNEMPLOYED = enum.auto()

class Household(NamedTuple):
    id: int
    account_id: int = None
    firm_id: int = None
    employment_contract_id: int = None
    employment_status: EmploymentStatus = EmploymentStatus.INVOLUNTARY_UNEMPLOYED
    reservation_wage: int = 0
    unemployment_duration: int = 0
    consumption_quantity: int = 0
    consumption_value: int = 0
    savings_target_ratio: Fraction = Fraction(5, 100)
    propensity_to_save: Fraction = Fraction(5, 100)
    propensity_to_consume_excess_savings: Fraction = Fraction(50, 100)
    wage_resistance: int = 12
    wage_flexibility: Fraction = Fraction(5, 100)
    job_search_size: int = 5
    purchase_search_size: int = 5
    income_history: list[int] = []

class EmploymentContract(NamedTuple):
    id: int
    household_id: int
    firm_id: int
    time_remaining: int
    wage: int

class Machine(NamedTuple): # Integrated
    id: int
    progress: int = 0
    value: int = 0
    production_time: int = 6
    productivity: int = 100

class Firm(NamedTuple):
    id: int
    account_id: int = None
    employment_contracts: dict[int, EmploymentContract] = {}
    employment_contracts_issued: int = 0
    hiring_vacancies: int = 10
    hiring_wage: int = 3_000_00
    hiring_wage_flex_up: Fraction = Fraction(6, 100)
    hiring_wage_flex_down: Fraction = Fraction(9, 100)
    hiring_wage_minimum: int = 0
    hiring_contract_length_minimum: int = 6
    hiring_contract_length_maximum: int = 18
    hiring_vacancy_rate_history: list[Fraction] = []
    hiring_vacancies_normal_rate: Fraction = Fraction(3, 100)
    machinery: dict[int, Machine] = {i : Machine(id=i) for i in range(10)}
    inventory_volume: int = 0
    inventory_value: int = 0
    inventory_for_sale_quantity: int = 0
    inventory_for_sale_unit_price: int = 0
    target_capital_ratio: Fraction = Fraction(10, 100)
    propensity_to_distribute_excess_capital: Fraction = Fraction(50, 100)
    target_inventory: int = 4_000
    propensity_to_sell: Fraction = Fraction(50, 100)
    price_flexibility: Fraction = Fraction(10, 100)
    target_utilization_ratio: Fraction = 0.5 + 0.5 * random()
    utilization_ratio_flexibility: Fraction = Fraction(10, 100)
    max_utilization_ratio: Fraction = Fraction(100, 100)

class Simulation(NamedTuple):
    bank: Bank = Bank()
    households: dict[int, Household] = {i : Household(id=i) for i in range(1_000)}
    firms: dict[int, Firm] = {i : Firm(id=i) for i in range(100)}

def new_sim():
    sim = Simulation()
    def bank_open_account_household(sim, household_id):
        account = Account(id = sim.bank.accounts_issued)
        return sim._replace(
            bank = sim.bank._replace(
                accounts_issued = sim.bank.accounts_issued + 1,
                accounts = {**sim.bank.accounts, account.id : account}
            ),
            households = {
                **sim.households,
                household_id : sim.households[household_id]._replace(account_id = account.id)
            }
        )
    sim = reduce(bank_open_account_household, sim.households.keys(), sim)
    def bank_open_account_firm(sim, firm_id):
        account = Account(id = sim.bank.accounts_issued)
        return sim._replace(
            bank = sim.bank._replace(
                accounts_issued = sim.bank.accounts_issued + 1,
                accounts = {**sim.bank.accounts, account.id : account}
            ),
            firms = {
                **sim.firms,
                firm_id : sim.firms[firm_id]._replace(account_id = account.id)
            }
        )
    sim = reduce(bank_open_account_firm, sim.firms.keys(), sim)
    return sim

def step(sim):
    sim = bank_pay_dividend(sim)
    sim = firms_pay_dividend(sim)
    sim = firms_plan_production(sim)
    sim = households_job_search(sim)
    sim = firms_production(sim)
    sim = households_consume(sim)
    sim = bank_debt_recovery(sim)
    sim = firms_layoff_bankrupt(sim)
    return sim

def account_debt(account):
    return sum([loan.principal for loan in account.loans.values()])

def bank_pay_dividend(sim):
    bank = sim.bank
    households = list(sim.households.values())
    dividend = bank_dividend(bank=bank)
    household = sample(households, 1)[0]
    # TODO we should not pay dividends to a bankrupt households!
    # TODO this is not how dividends are supposed to work!
    household_account = bank.accounts[household.account_id]
    return sim._replace(
        bank = bank._replace(
           capital = bank.capital - dividend,
           accounts = {
               **bank.accounts,
               **{
                   household_account.id : household_account._replace(
                       balance = household_account.balance + dividend
                   )
               }
           }
        )
    )

def bank_dividend(bank):
    assets = sum([account_debt(account) for account in bank.accounts.values()])
    required_capital = bank.target_capital_ratio * assets
    excedent_capital = max(0, bank.capital - required_capital)
    return floor(excedent_capital * bank.propensity_to_distribute_excess_capital)

def firms_pay_dividend(sim):
    firm_ids = [id for (id, firm) in sim.firms.items()
                if not sim.bank.accounts[firm.account_id].bankrupt]
    shuffle(firm_ids)
    return reduce(firm_pay_dividend, firm_ids, sim)

def firm_pay_dividend(sim, firm_id):
    firm = sim.firms[firm_id]
    firm_account = sim.bank.accounts[firm.account_id]
    dividend = firm_dividend(firm=firm, firm_account=firm_account)
    # TODO we should not pay dividends to a bankrupt households!
    # TODO this is not how dividends are supposed to work!
    households = list(sim.households.values())
    household = sample(households, 1)[0]
    household_account = sim.bank.accounts[household.account_id]
    return sim._replace(
        bank = sim.bank._replace(
           accounts = {
               **sim.bank.accounts,
               **{
                   household_account.id : household_account._replace(
                       balance = household_account.balance + dividend
                   ),
                   firm_account.id : firm_account._replace(
                       balance = firm_account.balance - dividend
                   )
               }
           }
        )
    )

def firm_dividend(firm, firm_account):
    assets = firm_account.balance + firm.inventory_value
    capital = assets - account_debt(firm_account)
    capital_target = firm.target_capital_ratio * assets
    excedent_capital = max(0, capital - capital_target)
    dividend = floor(excedent_capital * firm.propensity_to_distribute_excess_capital)
    return min(firm_account.balance, dividend)

def bank_lend(bank, account_id, principal):
    account = bank.accounts[account_id]
    loan = Loan(
        id = account.loans_issued,
        principal = principal,
        initial_value = principal,
        quality = LoanQuality.GOOD,
        interest_rate = bank.loan_normal_interest_rate,
        time_remaining = bank.loan_term,
        term = bank.loan_term
    )
    return bank._replace(
        accounts = {
            **bank.accounts,
            account_id: account._replace(
                loans_issued = account.loans_issued + 1,
                loans = {
                    **account.loans,
                    loan.id : loan
                },
                balance = account.balance + principal
            )
        }
    )

def firms_plan_production(sim):
    firm_ids = [firm.id for firm in sim.firms.values()
                if not sim.bank.accounts[firm.account_id].bankrupt]
    shuffle(firm_ids)
    return reduce(firm_plan_production, sim.firms.keys(), sim)

def firm_plan_production(sim, firm_id):
    bank = sim.bank
    firm = sim.firms[firm_id]

    inventory_ratio = Fraction(firm.inventory_volume, firm.target_inventory)

    # Determine production level
    max_production = sum([machine.productivity for machine in firm.machinery.values()])
    alpha1 = random()
    alpha2 = random()
    utilization_ratio_delta = alpha1 * firm.utilization_ratio_flexibility
    target_utilization_ratio = firm.target_utilization_ratio
    if inventory_ratio < 1 - alpha1 * alpha2:
        # Low level
        target_utilization_ratio += utilization_ratio_delta
    elif 1 + alpha1 * alpha2 < inventory_ratio:
        # High level
        target_utilization_ratio -= utilization_ratio_delta
    target_utilization_ratio = min(1, target_utilization_ratio, firm.max_utilization_ratio)

    # Determine price
    inventory_for_sale_unit_price = firm.inventory_for_sale_unit_price
    if inventory_for_sale_unit_price == 0:
        unit_cost = Fraction(firm.inventory_value, firm.inventory_volume or 1)
        inventory_for_sale_unit_price = 1 + 0.5 * random() * unit_cost
    else:
        alpha1 = random()
        alpha2 = random()
        if inventory_ratio < 1 - alpha1 * alpha2:
            # Low level
            inventory_for_sale_unit_price *= 1 + alpha1 * firm.price_flexibility
        elif 1 + alpha1 * alpha2 < inventory_ratio:
            # High level
            inventory_for_sale_unit_price *= 1 - alpha1 * firm.price_flexibility
    inventory_for_sale_unit_price = max(1, ceil(inventory_for_sale_unit_price))

    # Determine workforce
    target_employees = floor(len(firm.machinery) * target_utilization_ratio)
    current_employees = len([employment_contract
                             for employment_contract
                             in firm.employment_contracts.values()
                             if 0 < employment_contract.time_remaining])
    hiring_vacancies = target_employees - current_employees
    if hiring_vacancies < 0:
        to_fire_ids = sample(list(firm.employment_contracts.keys()), -hiring_vacancies)
        sim = reduce(lambda sim, employment_contract_id: firm_fire(sim, firm_id, employment_contract_id),
                     to_fire_ids,
                     sim)

    # Determine wage
    hiring_wage = firm.hiring_wage
    if 0 < hiring_vacancies:
        alpha1 = random()
        alpha2 = random()
        average_vacancy_rate = 0
        if 0 < len(firm.hiring_vacancy_rate_history):
          average_vacancy_rate = mean(firm.hiring_vacancy_rate_history)
        vacancy_ratio = Fraction(average_vacancy_rate, firm.hiring_vacancies_normal_rate)
        if vacancy_ratio < 1 - alpha1 * alpha2:
            # Low level
            hiring_wage *= 1 + alpha1 * firm.hiring_wage_flex_down
        elif 1 + alpha1 * alpha2 < vacancy_ratio:
            # High level
            hiring_wage *= 1 - alpha1 * firm.hiring_wage_flex_up
        hiring_wage = floor(max(hiring_wage, firm.hiring_wage_minimum))

    wage_budget = hiring_vacancies * hiring_wage + sum([employment_contract.wage
                                                     for employment_contract
                                                     in firm.employment_contracts.values()
                                                     if 0 < employment_contract.time_remaining])

    # Determine finance
    production_budget = wage_budget # No materials required, IntegratedFactory
    financing_need = production_budget - bank.accounts[firm.account_id].balance
    if 0 < financing_need:
        bank = bank_lend(bank=bank, account_id=firm.account_id, principal=financing_need)

    return sim._replace(
        bank = bank,
        firms = {
            **sim.firms,
            firm_id : firm._replace(
                target_utilization_ratio = target_utilization_ratio,
                inventory_for_sale_unit_price = inventory_for_sale_unit_price,
                hiring_vacancies = hiring_vacancies,
                hiring_wage = hiring_wage
            )
        }
    )

def firm_fire(sim, firm_id, employment_contract_id):
    firm = sim.firms[firm_id]
    employment_contract = firm.employment_contracts[employment_contract_id]
    household = sim.households[employment_contract.household_id]

    return sim._replace(
        firms = {
            **sim.firms,
            firm.id : firm._replace(
                employment_contracts = {contract for contract in firm.employment_contracts
                                        if contract.id != employment_contract.id}
            )
        },
        households = {
            **sim.households,
            household.id : household._replace(
                employment_contract_id = None,
                firm_id = None,
                employment_status = EmploymentStatus.INVOLUNTARY_UNEMPLOYED
            )
        }
    )

def households_job_search(sim):
    household_ids = [household.id for household in sim.households.values()
                     if not sim.bank.accounts[household.account_id].bankrupt]
    shuffle(household_ids)
    return reduce(household_job_search, household_ids, sim)

def household_job_search(sim, household_id):
    household = sim.households[household_id]

    employment_contract = None
    if household.firm_id and household.employment_contract_id:
      employment_contract = sim.firms[household.firm_id].employment_contracts[household.employment_contract_id]

    if employment_contract and employment_contract.time_remaining == 0:
        employment_contract = None

    reservation_wage = household.reservation_wage
    unemployment_duration = household.unemployment_duration
    if employment_contract:
        reservation_wage = employment_contract.wage
        unemployment_duration = 0
    else:
        unemployment_duration += 1
        alpha1 = random()
        alpha2 = random()
        if alpha1 * household.wage_resistance < unemployment_duration:
            reservation_wage *= 1 - household.wage_flexibility * alpha2

    employment_status = household.employment_status
    if employment_contract:
        employment_status = EmploymentStatus.EMPLOYED
    else:
        employment_status = EmploymentStatus.INVOLUNTARY_UNEMPLOYED
        employers = household_search_employers(sim, household)
        if 0 < len(employers):
          best_employer = employers[0]
          if reservation_wage <= best_employer.hiring_wage:
              sim = firm_hire_household(sim, best_employer.id, household_id)
              household = sim.households[household_id]
              employment_contract = sim.firms[household.firm_id].employment_contracts[household.employment_contract_id]
              employment_status = EmploymentStatus.EMPLOYED
          else:
              employment_status = EmploymentStatus.VOLUNTARY_UNEMPLOYED

    return sim._replace(
        households = {
            **sim.households,
            household_id : household._replace(
                employment_contract_id = employment_contract and employment_contract.id,
                reservation_wage = reservation_wage,
                unemployment_duration = unemployment_duration,
                employment_status = employment_status
            )
        }
    )

def household_search_employers(sim, household):
    hiring_firms = list(filter(
        lambda firm: not sim.bank.accounts[firm.account_id].bankrupt and 0 < firm.hiring_vacancies,
        sim.firms.values()
    ))
    found_firms = sample(hiring_firms, min(household.job_search_size, len(hiring_firms)))
    return sorted(found_firms, key=lambda firm: firm.hiring_wage, reverse=True)

def firm_hire_household(sim, firm_id, household_id):
    firm = sim.firms[firm_id]
    household = sim.households[household_id]
    employment_contract = EmploymentContract(
        id = firm.employment_contracts_issued,
        household_id = household_id,
        firm_id = firm_id,
        time_remaining = randrange(firm.hiring_contract_length_minimum, firm.hiring_contract_length_maximum + 1),
        wage = firm.hiring_wage
    )
    return sim._replace(
        firms = {
            **sim.firms,
            firm_id : firm._replace(
                employment_contracts = {
                    **firm.employment_contracts,
                    employment_contract.id : employment_contract
                },
                employment_contracts_issued = firm.employment_contracts_issued + 1,
                hiring_vacancies = firm.hiring_vacancies - 1
            )
        },
        households = {
            **sim.households,
            household_id : household._replace(
                firm_id = firm_id,
                employment_contract_id = employment_contract.id,
                employment_status = EmploymentStatus.EMPLOYED
            )
        }
    )

def firms_production(sim):
    firm_ids = [firm.id for firm in sim.firms.values()
                if not sim.bank.accounts[firm.account_id].bankrupt]
    shuffle(firm_ids)
    return reduce(firm_production, firm_ids, sim)

def firm_production(sim, firm_id):
    firm = sim.firms[firm_id]

    hiring_vacancy_rate = Fraction(firm.hiring_vacancies, len(firm.machinery))

    # Pay workers
    sim = reduce(lambda sim, employment_contract_id: firm_pay_worker(sim, firm_id, employment_contract_id),
                 firm.employment_contracts.keys(),
                 sim)

    # Produce
    def machine_sort_cmp(machine_x, machine_y):
        if machine_x.progress > machine_y.progress:
            return -1
        elif machine_x.progress < machine_y.progress:
            return 1
        elif machine_x.productivity > machine_y.productivity:
            return -1
        elif machine_x.productivity < machine_y.productivity:
            return 1
        else:
            return 0
    machinery = sorted(firm.machinery.values(), key=cmp_to_key(machine_sort_cmp))
    employees = [employment_contract
                 for employment_contract
                 in firm.employment_contracts.values()
                 if 0 < employment_contract.time_remaining]
    work_schedule = zip(machinery, employees)
    def machine_work(firm, machine_employee):
        machine, employment_contract = machine_employee
        progress = machine.progress + 1
        value = machine.value + employment_contract.wage
        inventory_value = firm.inventory_value
        inventory_volume = firm.inventory_volume
        if progress == machine.production_time:
            inventory_value += value
            inventory_volume += machine.productivity
            progress = 0
            value = 0
        return firm._replace(
            machinery = {
                **firm.machinery,
                machine.id : machine._replace(
                    progress = progress,
                    value = value,
                )
            },
            inventory_value = inventory_value,
            inventory_volume = inventory_volume
        )
    firm = reduce(machine_work, work_schedule, firm)

    # Offer goods
    max_production = sum([machine.productivity for machine in firm.machinery.values()])
    inventory_for_sale_quantity = floor(min(firm.inventory_volume * firm.propensity_to_sell,
                                    2 * max_production))

    return sim._replace(
        firms = {
            **sim.firms,
            firm.id : firm._replace(
                inventory_for_sale_quantity = inventory_for_sale_quantity,
                hiring_vacancy_rate_history = [*firm.hiring_vacancy_rate_history, hiring_vacancy_rate]
            )
        }
    )

def firm_pay_worker(sim, firm_id, employment_contract_id):
    firm = sim.firms[firm_id]
    firm_account = sim.bank.accounts[firm.account_id]
    employment_contract = firm.employment_contracts[employment_contract_id]
    household = sim.households[employment_contract.household_id]
    household_account = sim.bank.accounts[household.account_id]
    # TODO update wage bill and effective workforce?
    return sim._replace(
        bank = sim.bank._replace(
            accounts = {
                **sim.bank.accounts,
                firm_account.id : firm_account._replace(
                    balance = firm_account.balance - employment_contract.wage
                ),
                household_account.id : household_account._replace(
                    balance = household_account.balance + employment_contract.wage
                )
            }
        )
    )

def households_consume(sim):
    household_ids = [household.id for household in sim.households.values()
                     if not sim.bank.accounts[household.account_id].bankrupt]
    shuffle(household_ids)
    return reduce(household_consume, household_ids, sim)

def household_consume(sim, household_id):
    household = sim.households[household_id]
    account = sim.bank.accounts[household.account_id]

    average_income = 0
    if 0 < len(household.income_history):
      average_income = mean(household.income_history)
    savings_target = 12 * average_income * household.savings_target_ratio
    savings = account.balance - average_income
    consumption_target = 0
    if savings < savings_target:
        consumption_target = average_income * (1 - household.propensity_to_save)
    else:
        consumption_target = average_income + (savings - savings_target) * household.propensity_to_consume_excess_savings
    budget = min(account.balance, consumption_target)
    suppliers = household_search_suppliers(household, sim.firms)
    def purchase(state, household_id, firm):
        sim, budget = state
        household = sim.households[household_id]
        household_account = sim.bank.accounts[household.account_id]
        firm_account = sim.bank.accounts[firm.account_id]

        deal_volume = min(floor(budget / firm.inventory_for_sale_unit_price),
                          firm.inventory_for_sale_quantity)
        if deal_volume == 0:
          return (sim, budget)
        deal_value = deal_volume * firm.inventory_for_sale_unit_price
        inventory_unit_cost = Fraction(firm.inventory_value, firm.inventory_volume)
        deal_inventory_value = floor(inventory_unit_cost * deal_volume) # TODO safe to floor here?

        sim = sim._replace(
            bank = sim.bank._replace(
                accounts = {
                    **sim.bank.accounts,
                    household_account.id : household_account._replace(
                        balance = household_account.balance - deal_value
                    ),
                    firm_account.id : firm_account._replace(
                        balance = firm_account.balance + deal_value
                    )
                }
            ),
            firms = {
                **sim.firms,
                firm.id : firm._replace(
                    inventory_volume = firm.inventory_volume - deal_volume,
                    inventory_value = firm.inventory_value - deal_inventory_value,
                    inventory_for_sale_quantity = firm.inventory_for_sale_quantity - deal_volume
                )
            }
        )
        budget = budget - deal_value

        return (sim, budget)
    sim, remaining_budget = reduce(lambda state, firm: purchase(state, household_id, firm),
                                   suppliers,
                                   (sim, budget))

    return sim

def household_search_suppliers(household, firms):
    selling_firms = list(filter(
        lambda firm: 0 < firm.inventory_for_sale_unit_price,
        firms.values()
    ))
    found_firms = sample(selling_firms, household.purchase_search_size)
    return sorted(found_firms, key=lambda firm: firm.inventory_for_sale_unit_price, reverse=True)

def bank_debt_recovery(sim):
    account_ids = list(sim.bank.accounts.keys())
    shuffle(account_ids)
    return reduce(bank_debt_recovery_account, account_ids, sim)

def bank_debt_recovery_account(sim, account_id):
    bank = sim.bank
    account = bank.accounts[account_id]
    loans = list(account.loans.values())

    sim = reduce(lambda sim, loan_id: loan_pay_interest(sim, account_id, loan_id),
                 [loan.id for loan in loans],
                 sim)
    bank = sim.bank
    account = bank.accounts[account_id]
    loans = sorted(list(account.loans.values()), key=cmp_to_key(loan_cmp))
    sim = reduce(lambda sim, loan_id: loan_pay_back(sim, account_id, loan_id),
                 [loan.id for loan in loans],
                 sim)

    bank = sim.bank
    account = bank.accounts[account_id]
    loans = sorted(list(account.loans.values()), key=cmp_to_key(loan_cmp))
    if 0 < len(loans) and loans[0].quality == LoanQuality.BAD and not bank.accommodating:
        sim = reduce(lambda sim, loan_id: loan_cancel(sim, account_id, loan_id),
                     [loan.id for loan in loans],
                     sim)
        sim = sim._replace(
            bank = bank._replace(
                accounts = {
                    **bank.accounts,
                    account.id : account._replace(
                        bankrupt = True
                    )
                }
            )
        )

    return sim

def loan_pay_interest(sim, account_id, loan_id):
    bank = sim.bank
    account = bank.accounts[account_id]
    loan = account.loans[loan_id]

    interest = floor(loan.principal * loan.interest_rate)
    interest_payment = min(account.balance, interest)

    return sim._replace(
        bank = bank._replace(
            capital = bank.capital + interest_payment,
            accounts = {
                **bank.accounts,
                account.id : account._replace(
                    balance = account.balance - interest_payment,
                    loans = {
                        **account.loans,
                        loan.id : loan._replace(
                            principal = loan.principal + interest - interest_payment
                        )
                    }
                )
            }
        )
    )

def loan_cmp(loan_x, loan_y):
    quality_key = {
        LoanQuality.BAD: 1,
        LoanQuality.DOUBTFUL: 2,
        LoanQuality.GOOD: 3
    }
    if quality_key[loan_x.quality] < quality_key[loan_y.quality]:
        return -1
    elif quality_key[loan_x.quality] > quality_key[loan_y.quality]:
        return 1
    else:
        return loan_x.time_remaining - loan_y.time_remaining

def loan_pay_back(sim, account_id, loan_id):
    bank = sim.bank
    account = bank.accounts[account_id]
    loan = account.loans[loan_id]

    time_remaining = loan.time_remaining
    quality = loan.quality

    if quality == LoanQuality.GOOD and 0 < time_remaining:
        return sim

    repayment = min(account.balance, loan.principal)
    if time_remaining == 0 and account.balance < loan.principal:
        time_remaining += loan.term
        if quality == LoanQuality.GOOD:
            quality = LoanQuality.DOUBTFUL
        elif quality == LoanQuality.DOUBTFUL:
            quality = LoanQuality.BAD

    return sim._replace(
        bank = bank._replace(
            accounts = {
                **bank.accounts,
                account.id : account._replace(
                    balance = account.balance - repayment,
                    loans = {
                        **account.loans,
                        loan.id : loan._replace(
                            principal = loan.principal - repayment,
                            quality = quality,
                            time_remaining = time_remaining
                        )
                    }
                )
            }
        )
    )

def loan_cancel(sim, account_id, loan_id):
    bank = sim.bank
    account = bank.accounts[account_id]
    loan = account.loans[loan_id]

    principal = loan.principal
    capital = bank.capital
    bank_bankrupt = bank.bankrupt

    if capital < principal:
        bank_bankrupt = True
    capital -= min(capital, principal)
    principal -= min(capital, principal)

    return sim._replace(
        bank = bank._replace(
            bankrupt = bank_bankrupt,
            capital = capital,
            accounts = {
                **bank.accounts,
                account.id : account._replace(
                    loans = {
                        **account.loans,
                        loan.id : loan._replace(
                            principal = principal
                        )
                    }
                )
            }
        )
    )

def firms_layoff_bankrupt(sim):
    firm_ids = [firm.id for firm in sim.firms.values()
                if sim.bank.accounts[firm.account_id].bankrupt]
    return reduce(firm_layoff_bankrupt, firm_ids, sim)

def firm_layoff_bankrupt(sim, firm_id):
    firm = sim.firms[firm_id]
    sim = reduce(lambda sim, employment_contract_id: firm_fire(sim, firm_id, employment_contract_id),
                     firm.employment_contracts.keys(),
                     sim)

    return sim
