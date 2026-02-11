import streamlit as st
from database import (
    init_db,
    add_book,
    get_books_filtered,
    update_book_status,
    update_book,
    delete_book,
    get_status_counts,
    STATUSES,
)
# Page config
st.set_page_config(
    page_title="My Library Ledger",
    page_icon="📚",
    layout="wide"
)

# Initialize database
init_db()

st.title("📚 My Library Ledger")

# --- Statistics Section ---
st.subheader("Library Overview")
counts = get_status_counts()
cols = st.columns(5)
status_labels = {
    "OWNED": "📖 Owned",
    "WISHLIST": "🎁 Wishlist",
    "SUGGESTED": "💡 Suggested",
    "BORROWED": "📥 Borrowed",
    "LENT": "📤 Lent",
}
for i, status in enumerate(STATUSES):
    with cols[i]:
        st.metric(label=status_labels[status], value=counts[status])

st.divider()

# --- Add Book Section ---
with st.expander("➕ Add New Book", expanded=False):
    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input("Title *", placeholder="Enter book title")
            new_author = st.text_input("Author", placeholder="Enter author name")
            new_status = st.selectbox("Status", STATUSES, index=0)
        with col2:
            new_person = st.text_input(
                "Person",
                placeholder="Who suggested / borrowed from / lent to"
            )
            new_notes = st.text_area("Notes", placeholder="Any additional notes")

        submitted = st.form_submit_button("Add Book", type="primary")
        if submitted:
            if not new_title.strip():
                st.error("Title is required.")
            else:
                add_book(
                    title=new_title.strip(),
                    author=new_author.strip() if new_author else None,
                    status=new_status,
                    person=new_person.strip() if new_person else None,
                    notes=new_notes.strip() if new_notes else None,
                )
                st.success(f"Added '{new_title}' to your library!")
                st.rerun()

st.divider()

# --- Library Table Section ---
st.subheader("📖 My Library")

# Filters
filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
with filter_col1:
    search_term = st.text_input(
        "🔍 Search",
        placeholder="Search in title, author, person, notes...",
        label_visibility="collapsed"
    )
with filter_col2:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + STATUSES,
        label_visibility="collapsed"
    )
with filter_col3:
    sort_options = {
        "Date Added (Newest)": "date_added DESC",
        "Date Added (Oldest)": "date_added ASC",
        "Title (A-Z)": "title ASC",
        "Title (Z-A)": "title DESC",
        "Author (A-Z)": "author ASC",
        "Author (Z-A)": "author DESC",
    }
    sort_label = st.selectbox(
        "Sort by",
        list(sort_options.keys()),
        label_visibility="collapsed"
    )
    sort_by = sort_options[sort_label]

# Get filtered books
books = get_books_filtered(search_term, status_filter, sort_by)

if not books:
    st.info("No books found. Add your first book above!")
else:
    # Display books
    for book in books:
        with st.container():
            col_main, col_actions = st.columns([3, 2])

            with col_main:
                # Book info
                title_display = f"**{book['title']}**"
                if book["author"]:
                    title_display += f" by {book['author']}"
                st.markdown(title_display)

                # Status badge and person
                status_emoji = {
                    "OWNED": "📖",
                    "WISHLIST": "🎁",
                    "SUGGESTED": "💡",
                    "BORROWED": "📥",
                    "LENT": "📤",
                }
                info_parts = [f"{status_emoji.get(book['status'], '')} {book['status']}"]
                if book["person"]:
                    if book["status"] == "SUGGESTED":
                        info_parts.append(f"by {book['person']}")
                    elif book["status"] == "BORROWED":
                        info_parts.append(f"from {book['person']}")
                    elif book["status"] == "LENT":
                        info_parts.append(f"to {book['person']}")
                    else:
                        info_parts.append(f"({book['person']})")

                st.caption(" • ".join(info_parts))

                if book["notes"]:
                    st.caption(f"📝 {book['notes']}")

            with col_actions:
                action_cols = st.columns(4)

                # Quick action: Move to Owned (for Wishlist/Suggested)
                if book["status"] in ["WISHLIST", "SUGGESTED"]:
                    with action_cols[0]:
                        if st.button("✅ Own", key=f"own_{book['id']}", help="Move to Owned"):
                            update_book_status(book["id"], "OWNED", person="")
                            st.rerun()

                # Quick action: Mark Returned (for Borrowed/Lent)
                if book["status"] == "BORROWED":
                    with action_cols[0]:
                        if st.button("↩️ Return", key=f"return_{book['id']}", help="Mark as returned (now Owned)"):
                            update_book_status(book["id"], "OWNED", person="")
                            st.rerun()

                if book["status"] == "LENT":
                    with action_cols[0]:
                        if st.button("↩️ Got Back", key=f"gotback_{book['id']}", help="Mark as returned to you"):
                            update_book_status(book["id"], "OWNED", person="")
                            st.rerun()

                # Change status dropdown
                with action_cols[1]:
                    current_index = STATUSES.index(book["status"]) if book["status"] in STATUSES else 0
                    new_status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=current_index,
                        key=f"status_{book['id']}",
                        label_visibility="collapsed"
                    )

                with action_cols[2]:
                    if new_status != book["status"]:
                        if st.button("💾", key=f"save_{book['id']}", help="Save status change"):
                            update_book_status(book["id"], new_status)
                            st.rerun()

                # Edit button
                with action_cols[3]:
                    if st.button("✏️", key=f"edit_btn_{book['id']}", help="Edit book"):
                        st.session_state[f"editing_{book['id']}"] = True
                        st.rerun()

            # Edit form (shown when edit button clicked)
            if st.session_state.get(f"editing_{book['id']}", False):
                with st.form(f"edit_form_{book['id']}"):
                    st.markdown("**Edit Book**")
                    edit_col1, edit_col2 = st.columns(2)
                    with edit_col1:
                        edit_title = st.text_input("Title", value=book["title"])
                        edit_author = st.text_input("Author", value=book["author"] or "")
                        edit_status = st.selectbox(
                            "Status",
                            STATUSES,
                            index=STATUSES.index(book["status"]) if book["status"] in STATUSES else 0
                        )
                    with edit_col2:
                        edit_person = st.text_input("Person", value=book["person"] or "")
                        edit_notes = st.text_area("Notes", value=book["notes"] or "")

                    form_cols = st.columns([1, 1, 4])
                    with form_cols[0]:
                        save_edit = st.form_submit_button("Save", type="primary")
                    with form_cols[1]:
                        cancel_edit = st.form_submit_button("Cancel")

                    if save_edit:
                        if not edit_title.strip():
                            st.error("Title is required.")
                        else:
                            update_book(
                                book["id"],
                                edit_title.strip(),
                                edit_author.strip() if edit_author else None,
                                edit_status,
                                edit_person.strip() if edit_person else None,
                                edit_notes.strip() if edit_notes else None,
                            )
                            st.session_state[f"editing_{book['id']}"] = False
                            st.rerun()

                    if cancel_edit:
                        st.session_state[f"editing_{book['id']}"] = False
                        st.rerun()

                # Delete button (outside form, inside edit mode)
                if st.button("🗑️ Delete Book", key=f"delete_{book['id']}", type="secondary"):
                    delete_book(book["id"])
                    st.session_state[f"editing_{book['id']}"] = False
                