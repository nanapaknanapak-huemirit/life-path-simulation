#!/usr/bin/env python3
"""
Life Path Simulation - Predicting Outcomes of Key Life Decisions

An interactive decision-tree simulator that models the long-term impact
of education and economics choices on a person's life trajectory.

Run: python3 life_simulation.py
"""

from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

SIMULATION_YEARS_SHORT = 5
SIMULATION_YEARS_LONG = 20
MAX_LIFE_SCORE = 100

INFLATION_RATE = 0.025
MARKET_RETURN_RATE = 0.07
SAVINGS_GROWTH_RATE = 0.03

BASE_SALARY = 35_000
BASE_MONTHLY_EXPENSES = 2_200

RISK_MULTIPLIERS = {
    "very_low": 0.95,
    "low": 0.85,
    "medium": 0.70,
    "high": 0.50,
    "very_high": 0.35,
}

EDUCATION_DEBT_RATES = {
    "none": 0,
    "trade": 15_000,
    "bachelors": 45_000,
    "masters": 70_000,
    "phd": 55_000,
}


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ═══════════════════════════════════════════════════════════════════════════════

class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @staticmethod
    def disable():
        for attr in ("HEADER", "BLUE", "CYAN", "GREEN", "YELLOW", "RED",
                      "BOLD", "DIM", "UNDERLINE", "END"):
            setattr(Color, attr, "")


if os.name == "nt" or not sys.stdout.isatty():
    Color.disable()


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_divider(char: str = "─", width: int = 60):
    print(f"{Color.DIM}{char * width}{Color.END}")


def print_header(text: str):
    clear_screen()
    print()
    print_divider("═")
    print(f"{Color.BOLD}{Color.CYAN}  {text}{Color.END}")
    print_divider("═")
    print()


def print_section(text: str):
    print(f"\n{Color.BOLD}{Color.YELLOW}  ▸ {text}{Color.END}")
    print()


def print_info(label: str, value: Any):
    print(f"  {Color.DIM}{label}:{Color.END} {Color.BOLD}{value}{Color.END}")


def print_outcome(text: str, positive: bool = True):
    color = Color.GREEN if positive else Color.RED
    icon = "✓" if positive else "✗"
    print(f"  {color}{icon} {text}{Color.END}")


def print_prediction(text: str):
    print(f"  {Color.BLUE}~ {text}{Color.END}")


def print_warning(text: str):
    print(f"  {Color.YELLOW}⚠ {text}{Color.END}")


def pause():
    print(f"\n{Color.DIM}  Press Enter to continue...{Color.END}", end="")
    input()


def get_choice(max_options: int) -> int:
    while True:
        try:
            raw = input(f"\n  {Color.BOLD}Your choice [1-{max_options}]: {Color.END}").strip()
            choice = int(raw)
            if 1 <= choice <= max_options:
                return choice
            print(f"  {Color.RED}Please enter a number between 1 and {max_options}.{Color.END}")
        except ValueError:
            print(f"  {Color.RED}Invalid input. Enter a number.{Color.END}")


def format_currency(amount: float) -> str:
    if abs(amount) >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    if abs(amount) >= 1_000:
        return f"${amount / 1_000:.0f}K"
    return f"${amount:,.0f}"


def format_percentage(value: float) -> str:
    return f"{value:.0f}%"


# ═══════════════════════════════════════════════════════════════════════════════
# PERSON MODEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PersonState:
    """Tracks a person's life state throughout the simulation."""
    name: str = "You"
    age: int = 22
    education_level: str = "high_school"
    annual_salary: float = BASE_SALARY
    total_debt: float = 0.0
    savings: float = 0.0
    investment_portfolio: float = 0.0
    monthly_expenses: float = BASE_MONTHLY_EXPENSES
    job_satisfaction: float = 50.0
    financial_security: float = 30.0
    career_growth_potential: float = 50.0
    skill_adaptability: float = 50.0
    risk_tolerance: float = 50.0
    choices_made: list[dict] = field(default_factory=list)

    def add_debt(self, amount: float):
        self.total_debt += amount

    def reduce_debt(self, amount: float):
        self.total_debt = max(0, self.total_debt - amount)

    def add_savings(self, amount: float):
        self.savings += amount

    def add_investment(self, amount: float):
        self.investment_portfolio += amount

    def grow_investments(self, years: int):
        self.investment_portfolio *= (1 + MARKET_RETURN_RATE) ** years

    def grow_savings(self, years: int):
        self.savings *= (1 + SAVINGS_GROWTH_RATE) ** years

    def adjust_salary(self, multiplier: float):
        self.annual_salary *= multiplier

    def adjust_satisfaction(self, delta: float):
        self.job_satisfaction = max(0, min(100, self.job_satisfaction + delta))

    def adjust_security(self, delta: float):
        self.financial_security = max(0, min(100, self.financial_security + delta))

    def adjust_growth(self, delta: float):
        self.career_growth_potential = max(0, min(100, self.career_growth_potential + delta))

    def adjust_adaptability(self, delta: float):
        self.skill_adaptability = max(0, min(100, self.skill_adaptability + delta))

    @property
    def net_worth(self) -> float:
        return self.savings + self.investment_portfolio - self.total_debt

    @property
    def monthly_income(self) -> float:
        return self.annual_salary / 12

    @property
    def debt_to_income_ratio(self) -> float:
        if self.annual_salary == 0:
            return float("inf")
        return self.total_debt / self.annual_salary

    def record_choice(self, category: str, scenario: str, choice_label: str, effects: dict):
        self.choices_made.append({
            "category": category,
            "scenario": scenario,
            "choice": choice_label,
            "effects": effects,
        })

    def display_current_state(self):
        print_section("Current Life State")
        print_info("Age", f"{self.age} years")
        print_info("Education", self.education_level.replace("_", " ").title())
        print_info("Annual Salary", format_currency(self.annual_salary))
        print_info("Total Debt", format_currency(self.total_debt))
        print_info("Savings", format_currency(self.savings))
        print_info("Investments", format_currency(self.investment_portfolio))
        print_info("Net Worth", format_currency(self.net_worth))
        print()
        self._display_bar("Job Satisfaction", self.job_satisfaction, Color.GREEN)
        self._display_bar("Financial Security", self.financial_security, Color.CYAN)
        self._display_bar("Career Growth", self.career_growth_potential, Color.YELLOW)
        self._display_bar("Skill Adaptability", self.skill_adaptability, Color.BLUE)

    def _display_bar(self, label: str, value: float, color: str):
        filled = int(value / 10)
        bar = "█" * filled + "░" * (10 - filled)
        print(f"  {label:.<25} {color}{bar}{Color.END} {value:.0f}/100")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Choice:
    label: str
    description: str
    probability_success: float
    risk_level: str
    salary_multiplier: float
    debt_change: float
    savings_change: float
    investment_change: float
    satisfaction_delta: float
    security_delta: float
    growth_delta: float
    adaptability_delta: float
    education_change: str | None = None
    outcome_text: str = ""

    @property
    def risk_multiplier(self) -> float:
        return RISK_MULTIPLIERS.get(self.risk_level, 0.70)


@dataclass
class Scenario:
    title: str
    description: str
    choices: list[Choice]
    category: str = "general"


def build_education_scenarios() -> list[Scenario]:
    return [
        Scenario(
            title="1. High School Completion",
            description="You are 18. Do you finish high school or leave early?",
            category="education",
            choices=[
                Choice(
                    label="Graduate High School",
                    description="Complete your diploma and keep doors open.",
                    probability_success=0.92,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=5,
                    security_delta=10,
                    growth_delta=10,
                    adaptability_delta=5,
                    education_change="high_school",
                    outcome_text=(
                        "You graduate with a diploma. This opens access to "
                        "universities, trade schools, and most entry-level jobs. "
                        "Your baseline earning potential is set at $35,000/year."
                    ),
                ),
                Choice(
                    label="Drop Out",
                    description="Leave school to work or explore other paths.",
                    probability_success=0.35,
                    risk_level="high",
                    salary_multiplier=0.70,
                    debt_change=0,
                    savings_change=2_000,
                    investment_change=0,
                    satisfaction_delta=-10,
                    security_delta=-15,
                    growth_delta=-20,
                    adaptability_delta=-10,
                    education_change="drop_out",
                    outcome_text=(
                        "Without a diploma, your options narrow significantly. "
                        "You earn roughly 30% less over your lifetime and face "
                        "fewer career advancement opportunities."
                    ),
                ),
            ],
        ),
        Scenario(
            title="2. Post-Secondary Education",
            description="After high school, which path do you take?",
            category="education",
            choices=[
                Choice(
                    label="University (4-year degree)",
                    description="Pursue a bachelor's degree at a university.",
                    probability_success=0.78,
                    risk_level="medium",
                    salary_multiplier=1.45,
                    debt_change=EDUCATION_DEBT_RATES["bachelors"],
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=10,
                    security_delta=5,
                    growth_delta=15,
                    adaptability_delta=10,
                    education_change="bachelors",
                    outcome_text=(
                        "You invest 4 years and ~$45K in debt, but graduate with "
                        "a bachelor's degree. Median salary jumps to ~$50,750. "
                        "Long-term earnings premium over high school: +$1.2M."
                    ),
                ),
                Choice(
                    label="Trade School (1-2 years)",
                    description="Learn a skilled trade: electrician, plumbing, HVAC.",
                    probability_success=0.88,
                    risk_level="low",
                    salary_multiplier=1.25,
                    debt_change=EDUCATION_DEBT_RATES["trade"],
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=12,
                    security_delta=10,
                    growth_delta=5,
                    adaptability_delta=5,
                    education_change="trade",
                    outcome_text=(
                        "In 1-2 years you become a certified tradesperson. "
                        "Starting salary ~$43,750 with strong demand. Low debt, "
                        "fast entry into the workforce. Some physical wear over time."
                    ),
                ),
                Choice(
                    label="Gap Year (work/travel)",
                    description="Take a year off to gain life experience.",
                    probability_success=0.60,
                    risk_level="medium",
                    salary_multiplier=0.95,
                    debt_change=0,
                    savings_change=1_500,
                    investment_change=0,
                    satisfaction_delta=8,
                    security_delta=-5,
                    growth_delta=0,
                    adaptability_delta=8,
                    education_change="gap_year",
                    outcome_text=(
                        "You gain life experience but delay education. Some people "
                        "never return to school. You save a small amount but miss "
                        "a year of career momentum and compound growth."
                    ),
                ),
            ],
        ),
        Scenario(
            title="3. Field of Study",
            description="What do you focus your studies on?",
            category="education",
            choices=[
                Choice(
                    label="STEM (Science, Tech, Engineering, Math)",
                    description="Pursue a technical, high-demand field.",
                    probability_success=0.80,
                    risk_level="low",
                    salary_multiplier=1.35,
                    debt_change=0,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=5,
                    security_delta=10,
                    growth_delta=15,
                    adaptability_delta=12,
                    education_change=None,
                    outcome_text=(
                        "STEM skills are in high demand. Starting salary ~$68,000. "
                        "Strong job market, clear career paths, and excellent "
                        "remote work opportunities. Workload can be intense."
                    ),
                ),
                Choice(
                    label="Business & Finance",
                    description="Study business administration or finance.",
                    probability_success=0.75,
                    risk_level="medium",
                    salary_multiplier=1.20,
                    debt_change=0,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=3,
                    security_delta=5,
                    growth_delta=10,
                    adaptability_delta=8,
                    education_change=None,
                    outcome_text=(
                        "Business degrees offer versatility across industries. "
                        "Starting salary ~$58,000. Good for entrepreneurship "
                        "and management tracks. More competitive job market."
                    ),
                ),
                Choice(
                    label="Arts & Humanities",
                    description="Pursue creative or liberal arts studies.",
                    probability_success=0.65,
                    risk_level="high",
                    salary_multiplier=0.90,
                    debt_change=0,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=12,
                    security_delta=-5,
                    growth_delta=5,
                    adaptability_delta=10,
                    education_change=None,
                    outcome_text=(
                        "Arts and humanities build critical thinking and creativity. "
                        "Starting salary ~$42,000. Higher job satisfaction for those "
                        "passionate about the field, but fewer high-paying roles."
                    ),
                ),
            ],
        ),
        Scenario(
            title="4. Graduate Education",
            description="Should you pursue advanced degrees?",
            category="education",
            choices=[
                Choice(
                    label="Master's Degree (1-2 years)",
                    description="Specialize further with a master's degree.",
                    probability_success=0.82,
                    risk_level="low",
                    salary_multiplier=1.25,
                    debt_change=EDUCATION_DEBT_RATES["masters"],
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=8,
                    security_delta=5,
                    growth_delta=10,
                    adaptability_delta=5,
                    education_change="masters",
                    outcome_text=(
                        "A master's adds ~$15,000/year to your salary. Cost: ~$70K "
                        "in additional debt. ROI breaks even in ~5 years. "
                        "Opens senior and management positions."
                    ),
                ),
                Choice(
                    label="PhD (4-6 years)",
                    description="Commit to doctoral research.",
                    probability_success=0.55,
                    risk_level="high",
                    salary_multiplier=1.15,
                    debt_change=EDUCATION_DEBT_RATES["phd"],
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=15,
                    security_delta=-5,
                    growth_delta=8,
                    adaptability_delta=-5,
                    education_change="phd",
                    outcome_text=(
                        "A PhD is intellectually rewarding but long. Low stipend "
                        "during studies, late career start. Academic job market "
                        "is extremely competitive. Industry roles pay well."
                    ),
                ),
                Choice(
                    label="Enter Workforce Now",
                    description="Skip grad school and start earning immediately.",
                    probability_success=0.85,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=5_000,
                    investment_change=2_000,
                    satisfaction_delta=0,
                    security_delta=5,
                    growth_delta=0,
                    adaptability_delta=3,
                    education_change=None,
                    outcome_text=(
                        "You start earning 2-4 years earlier, building experience "
                        "and savings. No additional debt. Some roles require "
                        "advanced degrees, but experience often compensates."
                    ),
                ),
            ],
        ),
        Scenario(
            title="5. Continuous Learning",
            description="How do you invest in ongoing skill development?",
            category="education",
            choices=[
                Choice(
                    label="Active Certifications & Courses",
                    description="Regularly earn certifications and take courses.",
                    probability_success=0.90,
                    risk_level="very_low",
                    salary_multiplier=1.15,
                    debt_change=2_000,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=8,
                    security_delta=8,
                    growth_delta=12,
                    adaptability_delta=15,
                    education_change=None,
                    outcome_text=(
                        "Continuous learning keeps you competitive. Annual cost "
                        "~$2K in courses. Salary grows 15% faster. You adapt "
                        "to industry changes and stay relevant longer."
                    ),
                ),
                Choice(
                    label="Minimal Learning",
                    description="Learn only when forced by job requirements.",
                    probability_success=0.70,
                    risk_level="medium",
                    salary_multiplier=0.95,
                    debt_change=0,
                    savings_change=500,
                    investment_change=0,
                    satisfaction_delta=-5,
                    security_delta=-5,
                    growth_delta=-10,
                    adaptability_delta=-10,
                    education_change=None,
                    outcome_text=(
                        "Skills stagnate over time. Your industry evolves but "
                        "you don't. After 10 years, you become less competitive "
                        "and more vulnerable to automation and layoffs."
                    ),
                ),
            ],
        ),
    ]


def build_economics_scenarios() -> list[Scenario]:
    return [
        Scenario(
            title="1. Saving Habit",
            description="How much of your income do you save each month?",
            category="economics",
            choices=[
                Choice(
                    label="Save 20% of Income",
                    description="Aggressively save one-fifth of every paycheck.",
                    probability_success=0.85,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=8_000,
                    investment_change=2_000,
                    satisfaction_delta=-3,
                    security_delta=15,
                    growth_delta=5,
                    adaptability_delta=5,
                    outcome_text=(
                        "20% savings builds a strong safety net. Within 5 years "
                        "you have ~$50K saved. Emergency fund covers 6+ months. "
                        "Compound interest accelerates wealth over decades."
                    ),
                ),
                Choice(
                    label="Save 10% of Income",
                    description="Save a moderate portion of your income.",
                    probability_success=0.90,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=4_000,
                    investment_change=1_000,
                    satisfaction_delta=0,
                    security_delta=8,
                    growth_delta=3,
                    adaptability_delta=3,
                    outcome_text=(
                        "10% savings is responsible but slower to grow. "
                        "Emergency fund builds over 2 years. Comfortable "
                        "lifestyle with moderate financial security."
                    ),
                ),
                Choice(
                    label="Spend Freely",
                    description="Live paycheck to paycheck, spend what you earn.",
                    probability_success=0.40,
                    risk_level="very_high",
                    salary_multiplier=1.0,
                    debt_change=2_000,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=8,
                    security_delta=-20,
                    growth_delta=-5,
                    adaptability_delta=-8,
                    outcome_text=(
                        "No savings means zero safety net. One emergency "
                        "expense can cascade into debt. Lifestyle inflation "
                        "keeps you trapped on the earnings treadmill."
                    ),
                ),
            ],
        ),
        Scenario(
            title="2. Investment Timing",
            description="When do you start investing for the future?",
            category="economics",
            choices=[
                Choice(
                    label="Invest Early (age 22)",
                    description="Start investing immediately with compound interest.",
                    probability_success=0.88,
                    risk_level="low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=0,
                    investment_change=5_000,
                    satisfaction_delta=5,
                    security_delta=12,
                    growth_delta=10,
                    adaptability_delta=5,
                    outcome_text=(
                        "Starting at 22, compound interest is your superpower. "
                        "$5K/year at 7% return grows to ~$430K by 45. Starting "
                        "early matters more than the amount invested."
                    ),
                ),
                Choice(
                    label="Invest Later (age 32)",
                    description="Wait 10 years, then start investing.",
                    probability_success=0.75,
                    risk_level="medium",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=0,
                    investment_change=5_000,
                    satisfaction_delta=0,
                    security_delta=5,
                    growth_delta=5,
                    adaptability_delta=3,
                    outcome_text=(
                        "10 years of missed compounding costs you ~$380K in "
                        "potential portfolio growth. You invest more per month "
                        "to catch up, but time is the most valuable asset."
                    ),
                ),
                Choice(
                    label="Don't Invest",
                    description="Keep money in a checking account or under a mattress.",
                    probability_success=0.30,
                    risk_level="very_high",
                    salary_multiplier=1.0,
                    debt_change=1_000,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=0,
                    security_delta=-15,
                    growth_delta=-10,
                    adaptability_delta=-5,
                    outcome_text=(
                        "Inflation eats your savings at ~2.5%/year. Over 20 years, "
                        "your purchasing power drops by 40%. You work harder "
                        "for less. Retirement becomes a crisis."
                    ),
                ),
            ],
        ),
        Scenario(
            title="3. Career Path",
            description="How do you structure your working life?",
            category="economics",
            choices=[
                Choice(
                    label="Start a Business",
                    description="Launch your own company or startup.",
                    probability_success=0.35,
                    risk_level="very_high",
                    salary_multiplier=0.50,
                    debt_change=20_000,
                    savings_change=0,
                    investment_change=0,
                    satisfaction_delta=15,
                    security_delta=-15,
                    growth_delta=20,
                    adaptability_delta=12,
                    outcome_text=(
                        "High risk, high reward. 65% of startups fail in "
                        "the first 5 years. But successful founders earn "
                        "5-10x more than employees. Freedom and impact are unmatched."
                    ),
                ),
                Choice(
                    label="Stable Employment",
                    description="Work for an established company with benefits.",
                    probability_success=0.85,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=3_000,
                    investment_change=2_000,
                    satisfaction_delta=0,
                    security_delta=10,
                    growth_delta=5,
                    adaptability_delta=3,
                    outcome_text=(
                        "Steady paycheck, health insurance, 401(k) match. "
                        "Predictable career ladder. Less freedom but reliable "
                        "income. Average tenure: 3-5 years per employer."
                    ),
                ),
                Choice(
                    label="Freelancing",
                    description="Work independently, client by client.",
                    probability_success=0.55,
                    risk_level="high",
                    salary_multiplier=1.10,
                    debt_change=0,
                    savings_change=1_000,
                    investment_change=1_000,
                    satisfaction_delta=10,
                    security_delta=-10,
                    growth_delta=8,
                    adaptability_delta=12,
                    outcome_text=(
                        "Freedom and flexibility but income volatility. "
                        "No employer benefits, you handle taxes and insurance. "
                        "Top freelancers out-earn employees; most struggle."
                    ),
                ),
            ],
        ),
        Scenario(
            title="4. Housing Decision",
            description="Where do you live in your late 20s?",
            category="economics",
            choices=[
                Choice(
                    label="Buy Property",
                    description="Purchase a home with a mortgage.",
                    probability_success=0.78,
                    risk_level="medium",
                    salary_multiplier=1.0,
                    debt_change=150_000,
                    savings_change=-10_000,
                    investment_change=15_000,
                    satisfaction_delta=10,
                    security_delta=8,
                    growth_delta=5,
                    adaptability_delta=-5,
                    outcome_text=(
                        "Homeownership builds equity over time. Down payment "
                        "drains savings, but the mortgage payment builds an "
                        "asset. Property typically appreciates 3-5%/year."
                    ),
                ),
                Choice(
                    label="Rent an Apartment",
                    description="Continue renting, keep flexibility.",
                    probability_success=0.85,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=2_000,
                    investment_change=3_000,
                    satisfaction_delta=3,
                    security_delta=3,
                    growth_delta=5,
                    adaptability_delta=10,
                    outcome_text=(
                        "Renting preserves liquidity and flexibility. You can "
                        "invest the difference instead of tying it up in a home. "
                        "No maintenance costs, but no equity building either."
                    ),
                ),
                Choice(
                    label="Live with Family",
                    description="Stay with parents to save aggressively.",
                    probability_success=0.90,
                    risk_level="very_low",
                    salary_multiplier=1.0,
                    debt_change=0,
                    savings_change=8_000,
                    investment_change=5_000,
                    satisfaction_delta=-8,
                    security_delta=12,
                    growth_delta=3,
                    adaptability_delta=3,
                    outcome_text=(
                        "Maximum savings rate. You can save $20K+/year. "
                        "Financial independence comes faster, but social "
                        "and personal growth may be limited."
                    ),
                ),
            ],
        ),
        Scenario(
            title="5. Income Diversification",
            description="How do you structure your income streams?",
            category="economics",
            choices=[
                Choice(
                    label="Multiple Side Income Streams",
                    description="Build 2-3 additional income sources.",
                    probability_success=0.50,
                    risk_level="medium",
                    salary_multiplier=1.40,
                    debt_change=0,
                    savings_change=5_000,
                    investment_change=3_000,
                    satisfaction_delta=-5,
                    security_delta=10,
                    growth_delta=10,
                    adaptability_delta=12,
                    outcome_text=(
                        "Multiple income streams provide resilience. If one "
                        "dries up, others sustain you. Higher total income "
                        "but more time commitment and complexity."
                    ),
                ),
                Choice(
                    label="Single Focused Salary",
                    description="Focus all energy on your main career.",
                    probability_success=0.80,
                    risk_level="low",
                    salary_multiplier=1.15,
                    debt_change=0,
                    savings_change=3_000,
                    investment_change=2_000,
                    satisfaction_delta=5,
                    security_delta=5,
                    growth_delta=8,
                    adaptability_delta=3,
                    outcome_text=(
                        "Deep specialization can lead to promotions and "
                        "expertise. Single point of failure, but mastery "
                        "in one area has compounding career benefits."
                    ),
                ),
            ],
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION TREE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PredictionEngine:
    """Processes choices and predicts outcomes using weighted probabilities."""

    def __init__(self, person: PersonState):
        self.person = person
        self.prediction_log: list[str] = []

    def apply_choice(self, choice: Choice, scenario_title: str):
        """Apply a choice's effects to the person state with probability."""
        success = random.random() < choice.probability_success
        risk_mod = choice.risk_multiplier

        if success:
            self._apply_positive_effects(choice, risk_mod)
            self.prediction_log.append(
                f"  {Color.GREEN}✓{Color.END} {scenario_title}: "
                f"{Color.BOLD}{choice.label}{Color.END} — Success"
            )
        else:
            self._apply_negative_effects(choice, risk_mod)
            self.prediction_log.append(
                f"  {Color.YELLOW}~{Color.END} {scenario_title}: "
                f"{Color.BOLD}{choice.label}{Color.END} — Partial outcome"
            )

        self.person.record_choice(
            category=choice.risk_level,
            scenario=scenario_title,
            choice_label=choice.label,
            effects={
                "success": success,
                "salary_mult": choice.salary_multiplier,
                "debt": choice.debt_change,
            },
        )

    def _apply_positive_effects(self, choice: Choice, risk_mod: float):
        p = self.person
        p.adjust_salary(choice.salary_multiplier * risk_mod)
        p.add_debt(choice.debt_change * risk_mod)
        p.add_savings(choice.savings_change * risk_mod)
        p.add_investment(choice.investment_change * risk_mod)
        p.adjust_satisfaction(choice.satisfaction_delta)
        p.adjust_security(choice.security_delta)
        p.adjust_growth(choice.growth_delta)
        p.adjust_adaptability(choice.adaptability_delta)
        if choice.education_change:
            p.education_level = choice.education_change

    def _apply_negative_effects(self, choice: Choice, risk_mod: float):
        p = self.person
        degraded_mod = risk_mod * 0.6
        p.adjust_salary(choice.salary_multiplier * degraded_mod)
        p.add_debt(choice.debt_change * 1.3)
        p.add_savings(choice.savings_change * degraded_mod)
        p.add_investment(choice.investment_change * degraded_mod)
        p.adjust_satisfaction(choice.satisfaction_delta * 0.5)
        p.adjust_security(choice.security_delta * 1.2)
        p.adjust_growth(choice.growth_delta * 0.5)
        p.adjust_adaptability(choice.adaptability_delta * 0.5)
        if choice.education_change:
            p.education_level = choice.education_change

    def project_future(self, years: int) -> dict:
        """Project the person's state into the future without mutating it."""
        p = self.person
        salary_growth = 1.03 ** years
        inflation = (1 + INFLATION_RATE) ** years

        projected_salary = p.annual_salary * salary_growth
        projected_investments = p.investment_portfolio * (1 + MARKET_RETURN_RATE) ** years
        projected_savings = p.savings * (1 + SAVINGS_GROWTH_RATE) ** years
        projected_debt = p.total_debt * max(0, 1 - 0.10 * years)

        return {
            "years": years,
            "projected_salary": projected_salary,
            "real_salary": projected_salary / inflation,
            "net_worth": projected_savings + projected_investments - projected_debt,
            "total_debt": projected_debt,
            "savings": projected_savings,
            "investments": projected_investments,
        }

    def calculate_life_score(self) -> float:
        """Calculate a composite life score (0-100)."""
        p = self.person
        weights = {
            "financial": 0.30,
            "satisfaction": 0.20,
            "security": 0.20,
            "growth": 0.15,
            "adaptability": 0.15,
        }

        financial_score = min(100, max(0, 50 + (p.net_worth / 1000)))
        return (
            weights["financial"] * financial_score
            + weights["satisfaction"] * p.job_satisfaction
            + weights["security"] * p.financial_security
            + weights["growth"] * p.career_growth_potential
            + weights["adaptability"] * p.skill_adaptability
        )


# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class ResultsDashboard:
    """Displays simulation results and comparisons."""

    def __init__(self, person: PersonState, engine: PredictionEngine):
        self.person = person
        self.engine = engine

    def show_full_results(self):
        self._show_prediction_log()
        self.person.display_current_state()
        self._show_future_projections()
        self._show_life_score()
        self._show_choices_table()
        self._show_final_verdict()

    def _show_prediction_log(self):
        print_header("Prediction Log")
        for entry in self.engine.prediction_log:
            print(entry)

    def _show_future_projections(self):
        print_header("Future Projections")

        proj_5 = self.engine.project_future(SIMULATION_YEARS_SHORT)
        proj_20 = self.engine.project_future(SIMULATION_YEARS_LONG)

        print_section(f"{SIMULATION_YEARS_SHORT}-Year Outlook")
        print_info("Projected Salary", format_currency(proj_5["projected_salary"]))
        print_info("Real Salary (inflation-adjusted)", format_currency(proj_5["real_salary"]))
        print_info("Net Worth", format_currency(proj_5["net_worth"]))
        print_info("Total Debt", format_currency(proj_5["total_debt"]))
        print_info("Investment Portfolio", format_currency(proj_5["investments"]))

        print_section(f"{SIMULATION_YEARS_LONG}-Year Outlook")
        print_info("Projected Salary", format_currency(proj_20["projected_salary"]))
        print_info("Real Salary (inflation-adjusted)", format_currency(proj_20["real_salary"]))
        print_info("Net Worth", format_currency(proj_20["net_worth"]))
        print_info("Total Debt", format_currency(proj_20["total_debt"]))
        print_info("Investment Portfolio", format_currency(proj_20["investments"]))

        self._show_trajectory_chart(proj_5, proj_20)

    def _show_trajectory_chart(self, proj_5: dict, proj_20: dict):
        print_section("Wealth Trajectory")
        nw_5 = max(0, proj_5["net_worth"])
        nw_20 = max(0, proj_20["net_worth"])
        max_nw = max(nw_5, nw_20, 1)
        bar_5_len = int((nw_5 / max_nw) * 30)
        bar_20_len = int((nw_20 / max_nw) * 30)

        print(f"  Year  5: {Color.CYAN}{'█' * bar_5_len}{'░' * (30 - bar_5_len)}{Color.END} {format_currency(nw_5)}")
        print(f"  Year 20: {Color.GREEN}{'█' * bar_20_len}{'░' * (30 - bar_20_len)}{Color.END} {format_currency(nw_20)}")
        print()

    def _show_life_score(self):
        print_header("Life Score Assessment")
        score = self.engine.calculate_life_score()
        score_int = int(score)
        filled = score_int // 2
        bar = "█" * filled + "░" * (50 - filled)

        if score >= 75:
            color = Color.GREEN
            grade = "EXCELLENT"
        elif score >= 55:
            color = Color.CYAN
            grade = "GOOD"
        elif score >= 35:
            color = Color.YELLOW
            grade = "MODERATE"
        else:
            color = Color.RED
            grade = "AT RISK"

        print(f"  {color}{bar}{Color.END}")
        print(f"\n  Score: {color}{Color.BOLD}{score:.0f} / {MAX_LIFE_SCORE}{Color.END}")
        print(f"  Grade: {color}{Color.BOLD}{grade}{Color.END}")
        print()
        print_prediction(
            f"Based on your choices, your overall life trajectory is {grade.lower()}. "
            f"Score components: Financial 30%, Satisfaction 20%, Security 20%, "
            f"Growth 15%, Adaptability 15%."
        )

    def _show_choices_table(self):
        print_header("All Decisions Summary")
        print(f"  {'#':<4} {'Category':<12} {'Choice':<35} {'Impact'}")
        print_divider()
        for i, entry in enumerate(self.person.choices_made, 1):
            cat_color = Color.CYAN if "edu" in entry["category"] or i <= 5 else Color.GREEN
            cat_label = "EDU" if i <= 5 else "ECON"
            effects = entry["effects"]
            impact = "High Risk" if effects.get("salary_mult", 1) < 0.8 else "Balanced"
            if effects.get("salary_mult", 1) > 1.2:
                impact = "High Reward"
            print(
                f"  {i:<4} {cat_color}{cat_label:<12}{Color.END} "
                f"{Color.BOLD}{entry['choice']:<35}{Color.END} {impact}"
            )
        print()

    def _show_final_verdict(self):
        print_header("Final Verdict")
        p = self.person

        strengths = []
        weaknesses = []
        if p.job_satisfaction >= 60:
            strengths.append("High job satisfaction")
        elif p.job_satisfaction < 40:
            weaknesses.append("Low job satisfaction")
        if p.financial_security >= 60:
            strengths.append("Strong financial security")
        elif p.financial_security < 40:
            weaknesses.append("Weak financial safety net")
        if p.net_worth > 50_000:
            strengths.append("Positive net worth trajectory")
        elif p.net_worth < 0:
            weaknesses.append("Negative net worth")
        if p.career_growth_potential >= 60:
            strengths.append("Strong career growth potential")
        if p.skill_adaptability >= 60:
            strengths.append("Highly adaptable skill set")

        if strengths:
            print_section("Strengths")
            for s in strengths:
                print_outcome(s, positive=True)

        if weaknesses:
            print_section("Areas of Concern")
            for w in weaknesses:
                print_outcome(w, positive=False)

        print_section("Recommendation")
        if p.total_debt > p.annual_salary * 2:
            print_warning("Your debt load is high. Prioritize debt reduction before investing further.")
        if p.savings < p.monthly_expenses * 3:
            print_warning("Build an emergency fund covering 3-6 months of expenses.")
        if p.investment_portfolio < 10_000:
            print_warning("Consider starting investments — compound interest rewards early action.")
        if p.skill_adaptability < 40:
            print_warning("Invest in learning to stay competitive in a changing job market.")

        print()
        print_prediction(
            "Remember: these are probabilistic predictions. Your actual outcome "
            "depends on execution, timing, and opportunities you create."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATION CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════

class Simulation:
    """Main simulation orchestrator."""

    def __init__(self):
        self.person = PersonState()
        self.engine = PredictionEngine(self.person)
        self.education_scenarios = build_education_scenarios()
        self.economics_scenarios = build_economics_scenarios()

    def run(self):
        self._show_welcome()
        self._run_scenarios("Education", self.education_scenarios)
        self._run_scenarios("Economics", self.economics_scenarios)
        self.person.age = 42
        dashboard = ResultsDashboard(self.person, self.engine)
        dashboard.show_full_results()
        self._show_goodbye()

    def _show_welcome(self):
        clear_screen()
        print()
        print_divider("═")
        print(f"{Color.BOLD}{Color.CYAN}")
        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║        LIFE PATH SIMULATION — PREDICT YOUR FUTURE  ║")
        print("  ║                                                      ║")
        print("  ║   10 critical decisions • 2 domains • 1 life path    ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print(f"{Color.END}")
        print_divider("═")
        print()
        print(f"  {Color.DIM}This simulator models how education and economics")
        print(f"  choices compound over 20 years into life outcomes.")
        print(f"  Each choice carries probability and risk.{Color.END}")
        print()
        print_prediction("You are 22 years old, freshly out of high school.")
        print_prediction("Your journey begins now.")
        pause()

    def _run_scenarios(self, domain: str, scenarios: list[Scenario]):
        print_header(f"Phase: {domain} Decisions")

        domain_color = Color.CYAN if domain == "Education" else Color.GREEN
        print(f"  {domain_color}{Color.BOLD}{domain.upper()}{Color.END} — "
              f"{len(scenarios)} critical decisions to make")
        print()
        print_prediction(
            f"Your choices in {domain.lower()} will shape your career options, "
            f"earning potential, and life satisfaction."
        )
        pause()

        for scenario in scenarios:
            self._present_scenario(scenario, domain)

    def _present_scenario(self, scenario: Scenario, domain: str):
        print_header(f"{domain}: {scenario.title}")
        print(f"  {Color.BOLD}{scenario.description}{Color.END}")
        print()
        print_divider()

        for i, choice in enumerate(scenario.choices, 1):
            risk_color = {
                "very_low": Color.GREEN,
                "low": Color.GREEN,
                "medium": Color.YELLOW,
                "high": Color.RED,
                "very_high": Color.RED,
            }.get(choice.risk_level, Color.YELLOW)

            print(f"\n  {Color.BOLD}{Color.CYAN}[{i}]{Color.END} {Color.BOLD}{choice.label}{Color.END}")
            print(f"      {Color.DIM}{choice.description}{Color.END}")
            print(f"      Risk: {risk_color}{choice.risk_level.replace('_', ' ')}{Color.END}")
            print()
            print_prediction(choice.outcome_text)

        print_divider()
        print(f"\n  {Color.BOLD}Which path do you choose?{Color.END}")

        choice_idx = get_choice(len(scenario.choices)) - 1
        chosen = scenario.choices[choice_idx]

        print_section("Processing prediction...")
        self.engine.apply_choice(chosen, scenario.title)
        pause()

    def _show_goodbye(self):
        print()
        print_divider("═")
        print(f"{Color.BOLD}{Color.GREEN}")
        print("  Simulation complete. Your life path has been mapped.")
        print(f"  Run again to explore different choices!{Color.END}")
        print_divider("═")
        print()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    random.seed()
    try:
        sim = Simulation()
        sim.run()
    except KeyboardInterrupt:
        print(f"\n\n{Color.DIM}Simulation interrupted. Goodbye.{Color.END}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
