import streamlit as st
import json
import datetime
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import requests
import os
import random
from dotenv import load_dotenv

# -------------------- CONFIGURATION --------------------
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

REMINDER_FILE = "reminders.json"
EXPENSE_FILE = "expenses.csv"
CSV_FILE = "Bengaluru_Restaurants.csv"


# -------------------- CHART STYLING --------------------
def apply_chart_style():
    """Apply consistent dark, modern styling to all charts"""
    # Dark charcoal background that complements Streamlit
    plt.rcParams['figure.facecolor'] = '#1E1E1E'  # Dark charcoal background
    plt.rcParams['axes.facecolor'] = '#2D2D2D'  # Dark gray chart background
    plt.rcParams['axes.edgecolor'] = '#404040'  # Medium gray borders
    plt.rcParams['grid.color'] = '#404040'  # Medium gray grid
    plt.rcParams['text.color'] = '#E0E0E0'  # Light gray text
    plt.rcParams['axes.labelcolor'] = '#E0E0E0'
    plt.rcParams['xtick.color'] = '#B0B0B0'  # Light gray ticks
    plt.rcParams['ytick.color'] = '#B0B0B0'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titleweight'] = 'medium'
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.linestyle'] = '--'


# Call this once at the beginning
apply_chart_style()

# -------------------- STREAMLIT SETUP --------------------
st.set_page_config(page_title="Smart Life Hub", layout="wide")
st.sidebar.title("🌙 Smart Life Hub")


# -------------------- DATA MANAGERS --------------------
class ReminderManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                for task in data:
                    if "completed" not in task:
                        task["completed"] = False
                return data
        except FileNotFoundError:
            return []

    def save(self, tasks):
        with open(self.file_path, "w") as f:
            json.dump(tasks, f, indent=4)

    def add(self, task_text, date_time):
        tasks = self.load()
        tasks.append({
            "task": task_text.strip(),
            "time": date_time,
            "completed": False
        })
        self.save(tasks)

    def check_reminders(self):
        """Check and show notifications for due reminders"""
        tasks = self.load()
        now = datetime.datetime.now()
        notifications = []

        for task in tasks:
            if not task["completed"]:
                try:
                    task_time = datetime.datetime.strptime(task["time"], "%Y-%m-%d %H:%M")
                    if task_time <= now:
                        notifications.append(task["task"])
                except:
                    try:
                        task_time = datetime.datetime.strptime(task["time"], "%Y-%m-%d")
                        if task_time.date() <= now.date():
                            notifications.append(task["task"])
                    except:
                        continue

        return notifications


class ExpenseManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        try:
            df = pd.read_csv(self.file_path)
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=["Item", "Amount", "Date"])

    def save(self, df):
        # Just save as-is without datetime conversion
        df.to_csv(self.file_path, index=False)

    def add(self, item, amount, date_str):
        """Add expense with manually entered date string"""
        df = self.load()

        # Store date exactly as provided
        new_row = pd.DataFrame({
            "Item": [item],
            "Amount": [float(amount)],
            "Date": [date_str]  # Store as string, no datetime conversion
        })

        df = pd.concat([df, new_row], ignore_index=True)
        self.save(df)

    def get_spending_insights(self):
        """Simple spending insights without datetime operations"""
        df = self.load()

        if df.empty:
            return ["No expenses yet to analyze"]

        insights = []

        # Basic insights
        total = df["Amount"].sum()
        avg = df["Amount"].mean()
        item_count = len(df)

        insights.append(f"💰 Total spent: ₹{total:.2f}")
        insights.append(f"📊 Average per expense: ₹{avg:.2f}")
        insights.append(f"📝 Total expenses: {item_count}")

        if not df.empty:
            # Most expensive
            max_idx = df["Amount"].idxmax()
            max_item = df.loc[max_idx]
            insights.append(f"🔥 Most expensive: {max_item['Item']} - ₹{max_item['Amount']:.2f}")

            # Cheapest
            min_idx = df["Amount"].idxmin()
            min_item = df.loc[min_idx]
            insights.append(f"💸 Cheapest: {min_item['Item']} - ₹{min_item['Amount']:.2f}")

        return insights


class RestaurantManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        try:
            return pd.read_csv(self.file_path)
        except:
            return pd.DataFrame()

    def get_occasion_suggestions(self, occasion):
        """Get restaurant suggestions based on occasion"""
        suggestions = {
            "Romantic Dinner": ["Fine Dining", "Italian", "French", "Candle Light"],
            "Family Dinner": ["North Indian", "Chinese", "Multi-cuisine", "Vegetarian"],
            "Business Lunch": ["Quick Bites", "Cafe", "Sandwiches", "Salads"],
            "Birthday Party": ["Pub", "Barbeque", "Multi-cuisine", "Desserts"],
            "Quick Lunch": ["Fast Food", "South Indian", "Street Food", "Snacks"],
            "Date Night": ["Italian", "Chinese", "Continental", "Wine Bar"]
        }
        return suggestions.get(occasion, ["Indian", "Chinese", "Italian"])


# -------------------- NOTIFICATION SYSTEM --------------------
def show_notifications():
    """Display notifications at the top of the app"""
    rm = ReminderManager(REMINDER_FILE)
    notifications = rm.check_reminders()

    if notifications:
        with st.container():
            st.markdown("""
            <style>
            .notification {
                background-color: #2D2D2D;
                border-left: 5px solid #4ECDC4;
                padding: 12px;
                margin: 10px 0;
                border-radius: 6px;
                color: #E0E0E0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            </style>
            """, unsafe_allow_html=True)

            for notification in notifications:
                st.markdown(f'<div class="notification">🔔 {notification}</div>', unsafe_allow_html=True)


# -------------------- PAGE: HOME --------------------
def show_home():
    st.header("Welcome to Smart Life Hub! 🏠")

    # Show notifications at top
    show_notifications()

    # Quick stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Time", datetime.datetime.now().strftime("%H:%M:%S"))

    with col2:
        rm = ReminderManager(REMINDER_FILE)
        pending = sum(1 for t in rm.load() if not t["completed"])
        st.metric("Pending Reminders", pending)

    with col3:
        em = ExpenseManager(EXPENSE_FILE)
        df = em.load()
        total = df["Amount"].sum() if not df.empty and "Amount" in df.columns else 0
        st.metric("Total Expenses", f"₹{total:.2f}")

    st.markdown("---")

    # Features overview
    st.subheader("✨ Features")
    cols = st.columns(4)

    features = [
        ("📅 Reminders", "Smart notifications & tracking"),
        ("💰 Expenses", "Spending insights & analysis"),
        ("🌤 Weather", "Live weather updates"),
        ("🍽 Restaurants", "Occasion-based recommendations")
    ]

    for col, (icon, desc) in zip(cols, features):
        with col:
            st.markdown(f"### {icon}")
            st.write(desc)


# -------------------- PAGE: REMINDERS --------------------
def show_reminders():
    st.header("📅 Smart Reminders")

    # Show notifications
    show_notifications()

    rm = ReminderManager(REMINDER_FILE)
    tasks = rm.load()

    # Add new reminder
    with st.expander("➕ Add New Reminder", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            task_text = st.text_input("Reminder", placeholder="E.g., 'Call Mom'")
        with col2:
            task_date = st.date_input("Date", datetime.date.today())
            task_time = st.time_input("Time", datetime.time(9, 0))

        if st.button("Add Reminder", type="primary") and task_text:
            date_str = datetime.datetime.combine(task_date, task_time).strftime("%Y-%m-%d %H:%M")
            rm.add(task_text, date_str)
            st.success("✅ Reminder added!")
            st.rerun()

    # Task frequency bar chart - TALLER, NARROWER, BRIGHTER GREEN
    if tasks:
        st.subheader("📊 Reminder Frequency")

        task_names = [t["task"] for t in tasks]
        freq = Counter(task_names)

        # Make chart taller but narrower - better proportions
        fig, ax = plt.subplots(figsize=(7, 3.5))  # Narrower (7) but taller (3.5)

        # BRIGHTER GREEN with BLACK outline
        colors = ['#00FFAA' for _ in freq.keys()]  # Bright neon green
        bars = ax.bar(freq.keys(), freq.values(), color=colors,
                      edgecolor='black', linewidth=2, alpha=0.9)  # Black outline

        # Add subtle glow effect with brighter colors
        for i, bar in enumerate(bars):
            # Use bright green gradient
            bar.set_color(plt.cm.Greens(0.5 + i * 0.05))  # Brighter greens
            bar.set_edgecolor('black')  # Black outline
            bar.set_linewidth(1.5)

        ax.set_ylabel("Count", fontsize=10, labelpad=10, color='#E0E0E0')
        ax.yaxis.grid(True, linestyle='--', alpha=0.2, color='#404040')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#404040')
        ax.spines['bottom'].set_color('#404040')

        # Set tick colors for dark theme
        ax.tick_params(axis='x', colors='#B0B0B0', rotation=45, labelsize=9)
        ax.tick_params(axis='y', colors='#B0B0B0', labelsize=9)

        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(fontsize=9)

        # Adjust layout
        plt.tight_layout(pad=1.5)
        st.pyplot(fig, use_container_width=False)  # Don't use full width

    # Display reminders
    st.subheader("📋 Your Reminders")

    if not tasks:
        st.info("No reminders yet. Add one above!")
    else:
        view = st.radio("View:", ["All", "Pending", "Completed"], horizontal=True)

        filtered_tasks = tasks
        if view == "Pending":
            filtered_tasks = [t for t in tasks if not t["completed"]]
        elif view == "Completed":
            filtered_tasks = [t for t in tasks if t["completed"]]

        for i, task in enumerate(filtered_tasks):
            col1, col2, col3 = st.columns([4, 2, 1])

            with col1:
                status = "✅" if task["completed"] else "⏰"
                st.write(f"{status} {task['task']}")

            with col2:
                try:
                    dt = datetime.datetime.strptime(task["time"], "%Y-%m-%d %H:%M")
                    time_str = dt.strftime("%b %d, %I:%M %p")
                except:
                    time_str = task["time"]
                st.write(f"📅 {time_str}")

            with col3:
                if st.button("Toggle", key=f"toggle_{i}"):
                    # Mark as completed
                    task["completed"] = not task["completed"]
                    rm.save(tasks)
                    st.rerun()


# -------------------- PAGE: EXPENSES --------------------
def show_expenses():
    st.header("💰 Smart Expense Tracker")

    em = ExpenseManager(EXPENSE_FILE)

    # Tabs for different sections
    tab1, tab2 = st.tabs(["Add Expense", "Spending Insights"])

    with tab1:
        # Add expense with MANUAL date entry
        with st.expander("➕ Add Expense", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                item = st.text_input("Item", placeholder="E.g., Groceries, Zomato, Fuel")
            with col2:
                amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=10.0)
            with col3:
                # Manual date entry - no datetime module issues
                date_input = st.text_input("Date (YYYY-MM-DD)",
                                           value=datetime.date.today().isoformat(),
                                           placeholder="YYYY-MM-DD")

            if st.button("Add Expense", type="primary") and item and amount > 0 and date_input:
                # Simple validation for date format
                try:
                    # Just check if it looks like YYYY-MM-DD
                    if len(date_input) == 10 and date_input[4] == '-' and date_input[7] == '-':
                        em.add(item, amount, date_input)
                        st.success(f"✅ Added: {item} - ₹{amount:.2f} on {date_input}")
                        st.rerun()
                    else:
                        st.error("❌ Date must be in YYYY-MM-DD format")
                except Exception as e:
                    st.error(f"Error adding expense: {e}")

        # Display expenses
        df = em.load()
        if not df.empty:
            st.subheader("📋 Expense History")
            # Sort by date string (works because YYYY-MM-DD format sorts correctly)
            display_df = df.copy()
            if 'Date' in display_df.columns:
                display_df = display_df.sort_values("Date", ascending=False)
            st.dataframe(display_df)

    with tab2:
        # Insights
        st.subheader("💡 Smart Spending Insights")
        df = em.load()
        insights = em.get_spending_insights()

        for insight in insights:
            st.info(insight)

        # Simple bar chart without datetime operations
        if not df.empty:
            st.subheader("📈 Top Spending Categories")

            # Group by item
            item_totals = df.groupby("Item")["Amount"].sum().sort_values(ascending=False).head(10)

            if not item_totals.empty:
                fig, ax = plt.subplots(figsize=(8, 4))
                colors = ['#FF4081' for _ in range(len(item_totals))]
                bars = ax.bar(item_totals.index, item_totals.values,
                              color=colors, edgecolor='black', linewidth=1)

                ax.set_ylabel("Amount (₹)", color='#E0E0E0')
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{int(x):,}'))

                ax.tick_params(axis='x', rotation=45, colors='#B0B0B0')
                ax.tick_params(axis='y', colors='#B0B0B0')

                plt.tight_layout()
                st.pyplot(fig)


# -------------------- PAGE: WEATHER & NEWS --------------------
def show_weather_news():
    st.header("🌤 Weather & 📰 News")

    # Weather Section
    st.subheader("🌤 Live Weather")
    city = st.text_input("City", "Bangalore")

    if st.button("Get Weather") and WEATHER_API_KEY:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url).json()

            if response.get("cod") == 200:
                temp = response['main']['temp']
                humidity = response['main']['humidity']
                condition = response['weather'][0]['description'].title()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temperature", f"{temp}°C")
                with col2:
                    st.metric("Humidity", f"{humidity}%")
                with col3:
                    st.write(f"**Condition:** {condition}")
            else:
                st.error("City not found")
        except:
            st.error("Weather service unavailable")

    st.markdown("---")

    # News Section
    st.subheader("📰 Latest News")

    if st.button("Get News") and NEWS_API_KEY:
        try:
            url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q=india&language=en"
            response = requests.get(url).json()
            articles = response.get("results", [])[:5]

            for article in articles:
                st.write(f"**{article.get('title', 'No title')}**")
                st.write(f"_{article.get('description', '')}_")
                st.divider()
        except:
            st.error("News service unavailable")


# -------------------- PAGE: RESTAURANTS --------------------
def show_restaurants():
    st.header("🍽 Smart Restaurant Finder")

    rm = RestaurantManager(CSV_FILE)
    df = rm.load_data()

    if df.empty:
        st.error("Restaurant database not available")
        return

    # Smart suggestions section
    st.subheader("💡 Smart Suggestions")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Occasion-Based:**")
        occasions = ["Romantic Dinner", "Family Dinner", "Business Lunch",
                     "Birthday Party", "Quick Lunch", "Date Night"]
        occasion = st.selectbox("Select Occasion", occasions)

        if st.button("Find for Occasion"):
            suggestions = rm.get_occasion_suggestions(occasion)
            st.session_state.auto_search = suggestions[0]
            st.rerun()

    with col2:
        st.write("**Feeling Lucky:**")
        if st.button("🎲 I'm Feeling Lucky"):
            # Random but good restaurant
            good_restaurants = df[df['rating'] >= 4.0]
            if not good_restaurants.empty:
                random_rest = good_restaurants.sample(1).iloc[0]
                st.session_state.lucky_restaurant = random_rest
            else:
                st.session_state.lucky_restaurant = df.sample(1).iloc[0]
            st.rerun()

        if "lucky_restaurant" in st.session_state:
            r = st.session_state.lucky_restaurant
            st.success(f"**{r['name']}** ⭐ {r['rating']:.1f}")
            st.write(f"Cuisine: {r['cuisine']}")
            st.write(f"Address: {r['localAddress'][:50]}...")

    st.markdown("---")

    # Main search
    st.subheader("🔍 Search Restaurants")

    # Use auto-search or manual input
    default_search = st.session_state.get("auto_search", "Indian")
    cuisine = st.text_input("Cuisine or Type", value=default_search)

    col1, col2 = st.columns([2, 1])
    with col1:
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.1)

    with col2:
        price_filter = st.selectbox("Price Range", ["Any", "₹₹ (Budget)", "₹₹₹ (Moderate)", "₹₹₹₹ (Premium)"])

    if st.button("Search", type="primary"):
        # Filter by cuisine and rating
        mask = (df["cuisine"].str.contains(cuisine, case=False, na=False) |
                df["description"].str.contains(cuisine, case=False, na=False))
        mask &= df["rating"] >= min_rating

        results = df[mask]

        if results.empty:
            st.warning(f"No restaurants found for '{cuisine}'")

            # Suggest similar
            all_cuisines = df["cuisine"].str.split(",").explode().str.strip().unique()
            similar = [c for c in all_cuisines if cuisine.lower() in str(c).lower()]
            if similar:
                st.write("Try similar cuisines:")
                for sim in similar[:3]:
                    if st.button(f"🔍 {sim}"):
                        st.session_state.auto_search = sim
                        st.rerun()
        else:
            st.success(f"Found {len(results)} restaurants")

            # Sort and display
            results = results.sort_values("rating", ascending=False)

            for _, row in results.head(10).iterrows():
                with st.expander(f"{row['name']} ⭐ {row['rating']:.1f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Address:** {row['localAddress']}")
                        st.write(f"**Phone:** {row['phone']}")
                        st.write(f"**Cuisine:** {row['cuisine']}")
                    with col2:
                        if pd.notna(row['description']):
                            st.write(f"**Description:** {row['description'][:150]}...")


# -------------------- MAIN APP --------------------
pages = {
    "🏠 Home": show_home,
    "📅 Reminders": show_reminders,
    "💰 Expenses": show_expenses,
    "🌤 Weather & News": show_weather_news,
    "🍽 Restaurants": show_restaurants
}

# Sidebar navigation
page_name = st.sidebar.radio("Navigate", list(pages.keys()))

# Show selected page
st.title("🧠 Smart Life Hub Dashboard")
pages[page_name]()