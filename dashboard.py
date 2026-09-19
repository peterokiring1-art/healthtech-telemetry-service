    with st.form("login_form"):
        # 🔑 Form credentials input matrix
        username = st.text_input("Username Identifier")
        password = st.text_input("Security Password", type="password")
        submit_btn = st.form_submit_button("Verify Credentials & Unlock Portal")
        
        if submit_btn:
            token = authenticate_clinician(username, password)
            if token:
                st.session_state.jwt_token = token
                st.success("✅ Signature verified. Injecting secure state tokens...")
                st.rerun()
            else:
                st.error("❌ Access Denied: Invalid clinician credentials or API gateway offline.")
                
    # 💡 ADDITION: UI Link Placement for Forgot Password
    # This sits cleanly right under the form boundaries for quick visibility
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("🔒 *Need administrative assistance?*")
    with col_right:
        # Renders an interactive anchor link mimicking an icon button gateway
        if st.button("❓ Forgot Password / Reset Account"):
            st.info(
                "ℹ️ **Self-Service Reset System Initialization:**\n\n"
                "Please contact your hospital DevOps infrastructure engineer group or run "
                "the `telemetry_storage.db` hash script in your deployment terminal to "
                "safely overwrite the database credential matrix entries manually."
            )
