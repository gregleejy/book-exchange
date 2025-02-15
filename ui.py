import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid
from fuzzywuzzy import process
from app import friend_data, shop_items, study_groups, leaderboard_data

st.set_page_config(page_title="Book Exchange", layout="wide")

if "username" not in st.session_state:
    st.session_state["username"] = None
    st.session_state["preferences"] = None
    st.session_state["purchased_books"] = set()
    st.session_state["chat_history"] = []  # ✅ Initialize chat history
    st.session_state["active_tab"] = "Market"  # ✅ Ensure active tab is initialized

if st.session_state["username"] is None:
    st.title("📚 Welcome to the Book Exchange Platform")
    st.header("🔑 Login")
    username = st.text_input("Enter your name:")
    if st.button("Login"):
        response = requests.post("http://127.0.0.1:5000/login", json={"username": username})
        if response.status_code == 200:
            st.session_state["username"] = username
            st.success(response.json()["message"])
            st.rerun()
else:
    if st.session_state["preferences"] is None:
        st.title("📖 Select Your Book Preferences")
        categories = ["Fantasy", "Technology", "Fiction", "Science", "History", "Self-Help", "Business", "Finance"]
        selected_preferences = st.multiselect("Choose your preferred genres:", categories)

        if st.button("Save Preferences"):
            response = requests.post("http://127.0.0.1:5000/save_preferences", json={"username": st.session_state["username"], "preferences": selected_preferences})
            if response.status_code == 200:
                st.session_state["preferences"] = selected_preferences
                st.success("Preferences saved successfully!")
                st.rerun()
        
    else:
        st.sidebar.title("📚 Navigation")
        # Ensure the correct tab is set when redirected
        tab = st.sidebar.radio(
            "Go to", 
            ["Market", "Leaderboard", "Shop", "Friends", "Study Groups", "Scott Rizzgerald Chatbot"], 
            index=["Market", "Leaderboard", "Shop", "Friends", "Study Groups", "Scott Rizzgerald Chatbot"].index(st.session_state["active_tab"])
        )

        # Reset active_tab if the user manually switches tabs
        if tab != st.session_state["active_tab"]:
            st.session_state["active_tab"] = tab

        if tab == "Market":
            st.header("📖 Recommended Books for You")
            response = requests.get(f"http://127.0.0.1:5000/match_books?username={st.session_state['username']}")
            if response.status_code == 200:
                matched_books = response.json().get("matched_books", [])
                if not matched_books:
                    st.warning("⚠️ No book recommendations found. Try updating your preferences or asking Scott!")
            else:
                matched_books = []
                st.error("⚠️ Error fetching recommendations. Please try again later.")
            if matched_books:
                st.markdown("### 📚 Top 5 Recommended Books")
                cols = st.columns(5, gap="medium")
                
                for i, book in enumerate(matched_books[:5]):
                    with cols[i]:
                        st.markdown(
                            f"""
                            <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: #f8f9fa; width: 100%;'>
                                <h4 style='text-align: center; font-size: 18px; margin-bottom: 5px;'>{book['title']}</h4>
                                <p style='text-align: center; font-size: 16px; font-weight: bold; color: green; margin-bottom: 5px;'>💲 {book.get('price', 'N/A')}</p>
                                <p style='text-align: center; font-size: 14px; color: #6c757d; margin-bottom: 10px;'>{book.get('description', 'No description available')}</p>
                            """,
                            unsafe_allow_html=True
                        )
                        if st.button(f"Buy {book['title']}", key=f"buy_{i}"):
                            st.session_state["purchased_books"].add(book['title'])
                            st.success(f"✅ Purchased {book['title']}!")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No recommendations found. Try searching for a book or chatting with Scott!")                    
            st.subheader("🔍 Search for a Book")
            search_query = st.text_input("Enter book title:")
            if st.button("Search"):
                response = requests.get(f"http://127.0.0.1:5000/search_book?title={search_query}")
                if response.status_code == 200:
                    book_result = response.json()["book"]
                    if book_result:
                        st.write("### Search Result:")
                        st.markdown(f"**{book_result['title']}**")
                        st.caption(f"💲 {book_result['price']}")
                        st.write(book_result['description'])
                    else:
                        st.warning("⚠️ No matching book found. Try chatting with Scott!")
            if st.button("🤖 Ask Scott for Help", key="ask_scott_redirect"):
                st.session_state["active_tab"] = "Scott Rizzgerald Chatbot"
                st.rerun()  # Ensures immediate redirection

            st.subheader("📢 Sell a Book")

            title = st.text_input("Book Title:")
            description = st.text_area("Book Description:")
            price = st.number_input("Set Price:", min_value=1, step=1, key="sell_price")

            # Two buttons: "List for Sale" and "Donate"
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📢 List for Sale", key="sell_book_button"):
                    response = requests.post("http://127.0.0.1:5000/market/add", json={
                        "username": st.session_state["username"], 
                        "title": title, 
                        "description": description, 
                        "price": price
                    })
                    if response.status_code == 200:
                        st.success("✅ Your book is now listed in the market!")

            with col2:
                if st.button("🎁 Donate (Earn 50 Points)", key="donate_book_button"):
                    response = requests.post("http://127.0.0.1:5000/market/add", json={
                        "username": st.session_state["username"], 
                        "title": title, 
                        "description": description, 
                        "price": 0  # Indicating donation
                    })
                    if response.status_code == 200:
                        # Add 50 points to user
                        points_update = requests.post("http://127.0.0.1:5000/update_points", json={
                            "username": st.session_state["username"], 
                            "points": 50
                        })
                        if points_update.status_code == 200:
                            st.session_state["user_points"] = points_update.json().get("points", 0)  # Update points in session
                            st.success("🎉 You have successfully donated this book and earned **50 points**! 🎁")
        if tab == "Shop":
            st.header("🛍️ Redeem Rewards with Points")

            # Fetch user's points (assumed session state tracks points)
            user_points = st.session_state.get("user_points", 0)

            # Display available rewards
            st.markdown(f"**💰 Your Current Points: {user_points}**")
            st.info("✨ Earn 500 points to redeem a free **Popular/Kinokuniya voucher**!")

            cols = st.columns(2, gap="large")  # Two-column layout

            for i, item in enumerate(shop_items):
                with cols[i % 2]:  # Alternating columns
                    st.markdown(
                        f"""
                        <div style='text-align: center; padding: 15px; border-radius: 10px; background-color: #f8f9fa; width: 100%;'>
                            <h4 style='text-align: center; font-size: 18px; margin-bottom: 5px;'>{item['item']}</h4>
                            <p style='text-align: center; font-size: 16px; font-weight: bold; color: red; margin-bottom: 10px;'>🔴 {item['points']} Points</p>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Redeem", key=f"redeem_{i}"):
                        if user_points >= item["points"]:
                            user_points -= item["points"]  # Deduct points
                            st.session_state["user_points"] = user_points
                            st.success(f"✅ Successfully redeemed: {item['item']}!")
                        else:
                            st.error("❌ Not enough points to redeem this item.")
                    st.markdown("</div>", unsafe_allow_html=True)
        elif tab == "Friends":
            st.header("👥 Find and Connect with Friends")

            # 🔍 Search for a Friend
            st.subheader("🔍 Search for a Friend")
            friend_search = st.text_input("Enter a friend's name:")

            if friend_search:
                matched_friend = next((f for f in friend_data if f["name"].lower() == friend_search.lower()), None)
                if matched_friend:
                    st.success(f"✅ Friend found: **{matched_friend['name']}**")
                    st.write(f"📖 **Currently:** {matched_friend['status']}")
                else:
                    st.warning("⚠️ Friend not found.")

            # 🎯 AI Matching - Call API for Top 5 Recommended Friends
            user_preferences = st.session_state.get("preferences", [])
            matched_friends = []

            if user_preferences:
                response = requests.post("http://127.0.0.1:5000/recommend_friends", json={"preferences": user_preferences})

                if response.status_code == 200:
                    matched_friends = response.json().get("matched_friends", [])
                else:
                    st.error("⚠️ Failed to fetch recommendations. Check backend.")

            st.markdown("### 🎯 **AI-Recommended Friends Based on Your Interests**")
            if matched_friends:
                cols = st.columns(min(5, len(matched_friends)), gap="medium")
                for i, friend in enumerate(matched_friends):
                    with cols[i]:
                        st.markdown(
                            f"""
                            <div style='text-align: center; padding: 15px; border-radius: 10px; background-color: #f8f9fa; width: 100%;'>
                                <h4 style='text-align: center; font-size: 18px; margin-bottom: 5px;'>{friend['name']}</h4>
                                <p style='text-align: center; font-size: 14px; color: #6c757d; margin-bottom: 5px;'>📌 {", ".join(friend.get("preferences", []))}</p>
                                <p style='text-align: center; font-size: 14px; font-weight: bold; color: green; margin-bottom: 10px;'>{friend['status']}</p>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(f"📚 Trade Book", key=f"trade_{i}"):
                            st.success(f"✅ Trade request sent to {friend['name']}!")

                        if st.button(f"👋 Bump", key=f"bump_{i}"):
                            st.success(f"💡 You just bumped {friend['name']}!")

                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("💡 No friend recommendations yet. Try updating your book preferences!")

            # 🟢 Friend Activity - Who's Online?
            st.subheader("🟢 Friend Activity - Who's Online?")
            online_friends = [f for f in friend_data if "Online" in f["status"]]
            offline_friends = [f for f in friend_data if "Last seen" in f["status"]]

            cols = st.columns(2, gap="large")  # Two-column layout for online/offline friends

            with cols[0]:  # Online Friends
                st.markdown("### 🟢 Currently Online")
                if online_friends:
                    for friend in online_friends:
                        st.write(f"✅ **{friend['name']}** - {friend['status']}")
                else:
                    st.warning("No friends are online right now.")

            with cols[1]:  # Offline Friends
                st.markdown("### 🔴 Last Seen")
                if offline_friends:
                    for friend in offline_friends:
                        st.write(f"❌ **{friend['name']}** - {friend['status']}")
                else:
                    st.warning("All your friends are currently online!")
        elif tab == "Study Groups":
            st.header("📚 Study Groups")

            # Display Study Groups
            for group in study_groups:
                with st.expander(f"📚 {group['group_name']} - {group['active_status']}"):
                    st.markdown(f"👥 **Members:** {', '.join(group['members'])}")
                    st.markdown(f"💬 **Discussion Topic:** {group['discussion_topic']}")
                    
                    # Display books being shared in a proper format
                    shared_books = [f"{entry['user']} is sharing '{entry['book']}'" for entry in group['book_sharing']]
                    st.markdown(f"📖 **Books Shared:** {', '.join(shared_books)}")

                    # Join Group Button
                    if st.button(f"Join {group['group_name']}", key=f"join_{group['group_name']}"):
                        st.success(f"✅ You joined **{group['group_name']}**! Start discussing now.")

                    # Start Discussion Button
                    if st.button(f"Start Discussion in {group['group_name']}", key=f"discuss_{group['group_name']}"):
                        st.text_area(f"💬 Share your thoughts in **{group['group_name']}**:")


        elif tab == "Leaderboard":
            st.header("🏆 Leaderboard")

            # Fetch user points
            response = requests.get(f"http://127.0.0.1:5000/user_points?username={st.session_state['username']}")
            if response.status_code == 200:
                user_points = response.json().get("points", 0)
            else:
                user_points = 470  # Default to 0 if error

            # Display current points in a styled container
            st.markdown(
                f"""
                <div style="padding: 15px; border-radius: 10px; background-color: #f8f9fa; 
                            text-align: center; font-size: 20px; font-weight: bold;">
                    🎯 Your Current Points: <span style="color: green;">{user_points}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Reward Prompt
            if user_points < 500:
                st.markdown(
                    f"""
                    <div style="padding: 10px; margin-top: 10px; border-radius: 8px; 
                                background-color: #fff3cd; color: #856404; text-align: center;">
                        🏅 Earn <b>{500 - user_points} more points</b> to get a 
                        <b>free Kinokuniya/Popular voucher!</b> 🎁
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="padding: 10px; margin-top: 10px; border-radius: 8px; 
                                background-color: #d4edda; color: #155724; text-align: center;">
                        🎉 Congratulations! You've earned a <b>free Kinokuniya/Popular voucher!</b> 🏅
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Styled Leaderboard Data
            df_leaderboard = pd.DataFrame(leaderboard_data)

            # Leaderboard Section Title
            st.markdown("### 🏅 Top Users")

            # Apply the same styling as book recommendations (styled table)
            cols = st.columns(5, gap="medium")
            
            for i, row in enumerate(df_leaderboard.itertuples()):
                with cols[i]:
                    st.markdown(
                        f"""
                        <div style='text-align: center; padding: 20px; border-radius: 10px; 
                                    background-color: #f8f9fa; width: 100%;'>
                            <h4 style='text-align: center; font-size: 18px; margin-bottom: 5px;'>🏆 Rank {row.Rank}</h4>
                            <p style='text-align: center; font-size: 16px; font-weight: bold; color: #007bff;'>
                                👤 {row.Username}</p>
                            <p style='text-align: center; font-size: 16px; font-weight: bold; color: green;'>
                                {row.Points} Points</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        elif tab == "Scott Rizzgerald Chatbot":
            st.header("🤖 Chat with Scott Rizzgerald")

            user_input = st.text_input("Scott: What kind of book are you looking for today?")

            if user_input:
                st.session_state["chat_history"].append(user_input)

            if st.button("Get Recommendations"):
                full_response = " ".join(st.session_state["chat_history"])
                response = requests.post("http://127.0.0.1:5000/chat_recommendations", json={"conversation": full_response})
                
                if response.status_code == 200:
                    response_data = response.json()
                    recommendations = response_data.get("matched_books", [])  # ✅ Ensure key exists
                else:
                    recommendations = []

                if recommendations:
                    st.markdown("### 📚 Scott's Top Book Recommendations")
                    cols = st.columns(5, gap="medium")

                    for i, book in enumerate(recommendations[:5]):
                        with cols[i]:
                            st.markdown(
                                f"""
                                <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: #f8f9fa; width: 100%;'>
                                    <h4 style='text-align: center; font-size: 18px; margin-bottom: 5px;'>{book.get('title', 'Unknown Title')}</h4>
                                    <p style='text-align: center; font-size: 16px; font-weight: bold; color: green; margin-bottom: 5px;'>💲 {book.get('price', 'N/A')}</p>
                                    <p style='text-align: center; font-size: 14px; color: #6c757d; margin-bottom: 10px;'>{book.get('description', 'No description available')}</p>
                                """,
                                unsafe_allow_html=True
                            )
                            if st.button(f"Buy {book['title']}", key=f"buy_chatbot_{i}"):
                                st.session_state["purchased_books"].add(book['title'])
                                st.success(f"✅ Purchased {book['title']}!")
                            st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No recommendations found. Try providing more details.")

                st.session_state["chat_history"] = []  # Reset chat after getting recommendations