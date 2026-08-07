# --- TAB 4: Data Map (PATH C) ---
with tab_datamap:
    st.subheader("Manage E2A Data Map (PATH C)")
    try:
        # 1. Fetch current data
        datamap_df = conn.query("SELECT * FROM tbl_data_map ORDER BY datasource_id", ttl="0s")
        
        # 2. Render Data Editor
        edited_datamap = st.data_editor(
            datamap_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_datamap", # This key stores the changes in st.session_state
            column_config={
                "datasource_id": st.column_config.NumberColumn("ID", disabled=True),
                "datasource_visiblestatus": st.column_config.CheckboxColumn("Visible?", default=True),
            }
        )
        
        # 3. Database Write-Back Logic
        if st.button("💾 Save Data Map Changes"):
            # Retrieve the dictionary of changes tracked by the editor's key
            changes = st.session_state["editor_datamap"]
            
            with conn.session as s:
                # Handle Deletions
                for row_idx in changes.get("deleted_rows", []):
                    # Get the ID of the deleted row from the original dataframe
                    row_id = int(datamap_df.iloc[row_idx]["datasource_id"])
                    s.execute(text("DELETE FROM tbl_data_map WHERE datasource_id = :id"), {"id": row_id})
                
                # Handle Updates (Edits)
                for row_idx, updates in changes.get("edited_rows", {}).items():
                    row_id = int(datamap_df.iloc[row_idx]["datasource_id"])
                    # Dynamically build the SET clause for updated columns
                    set_clauses = ", ".join([f"{col} = :{col}" for col in updates.keys()])
                    if set_clauses:
                        updates["id"] = row_id
                        query = text(f"UPDATE tbl_data_map SET {set_clauses} WHERE datasource_id = :id")
                        s.execute(query, updates)
                
                # Handle Insertions (New Rows)
                for new_row in changes.get("added_rows", []):
                    # Exclude the ID column since it's a SERIAL primary key in Neon DB
                    if "datasource_id" in new_row:
                        del new_row["datasource_id"]
                        
                    cols = ", ".join(new_row.keys())
                    vals = ", ".join([f":{col}" for col in new_row.keys()])
                    if cols:
                        query = text(f"INSERT INTO tbl_data_map ({cols}) VALUES ({vals})")
                        s.execute(query, new_row)
                
                # Commit all transactions to the Neon database
                s.commit()
            
            st.success("Data Map changes saved successfully to the database!")
            # Rerun the app to refresh the dataframe with new IDs from the database
            st.rerun()

    except Exception as e:
        st.error(f"Error executing database operations: {e}")
