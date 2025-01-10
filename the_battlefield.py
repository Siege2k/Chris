import streamlit as st
import random

# Initialize session state for combatants if not present
if "combatants" not in st.session_state:
    st.session_state.combatants = []

# Sidebar input fields
with st.sidebar:
    st.header("Add Combatants")
    name = st.text_input("Name")
    hp = st.number_input("HP", min_value=0, max_value=999, step=1)
    ac = st.number_input("AC", min_value=0, max_value=50, step=1)
    
    # Manual initiative input
    initiative = st.number_input("Initiative", min_value=0, max_value=30, step=1)
    
    # Button to roll initiative without modifying the manual field automatically
    if st.button("Roll Initiative"):
        rolled_initiative = random.randint(1, 20)
        st.write(f"Rolled Initiative: **{rolled_initiative}**")
    
    # Add combatant to session state
    if st.button("Add Combatant"):
        if name and initiative >= 0:
            # Add the combatant with max_hp set to the initial HP entered
            st.session_state.combatants.append({
                "name": name,
                "hp": hp,  # current HP
                "max_hp": hp,  # maximum HP
                "ac": ac,
                "initiative": initiative
            })
            st.success(f"Added {name} with initiative {initiative}")
        else:
            st.error("Please provide a valid name and initiative.")

# Display combatants added so far
st.subheader("Combatants in Battlefield")
for combatant in st.session_state.combatants:
    combatant_name = combatant['name']
    max_hp = combatant['max_hp']
    
    # Limit HP to the max_hp value
    combatant['hp'] = min(combatant['hp'], max_hp)
    
    # Display the combatant with current HP and max HP
    st.write(f"**{combatant_name}** - HP: {combatant['hp']} / {combatant['max_hp']}, AC: {combatant['ac']}, Initiative: {combatant['initiative']}")

import streamlit as st
import random

# Define the conditions dictionary
conditions = {
    "No Condition": "✅ No active conditions",
    "Bane": "🎲 Subtracts 1d4 from attack rolls and saving throws.",
    "Blessed": "✨ Bonus 1d4 to attack rolls and saving throws.",
    # Add more conditions as needed
}

# Ensure a default list in session state for combatants
if 'combatants' not in st.session_state:
    st.session_state['combatants'] = []

# Initialize turn and round trackers
if 'current_turn_index' not in st.session_state:
    st.session_state['current_turn_index'] = 0
if 'round' not in st.session_state:
    st.session_state['round'] = 1

st.subheader("The Battlefield")

if not st.session_state['combatants']:
    st.write("No combatants added. Use the sidebar to add combatants.")
else:
    # Sort combatants by initiative
    sorted_combatants = sorted(
        st.session_state['combatants'],
        key=lambda x: (-x['initiative'], st.session_state['combatants'].index(x))
    )

    st.write(f"Round: {st.session_state['round']}")
    st.write(f"Current Turn: **{sorted_combatants[st.session_state['current_turn_index']]['name']}**")

    # Display each combatant
    for i, combatant in enumerate(sorted_combatants):
        combatant_name = combatant['name']
        max_hp = combatant.get('max_hp', combatant['hp'])  # Assume max_hp if provided
        hp_emoji = "🩸" if combatant['hp'] <= max_hp / 2 else ""
        conditions_emoji = " ".join([conditions[cond].split()[0] for cond in combatant.get('conditions', ['No Condition'])])
        turn_marker = "➡️" if i == st.session_state['current_turn_index'] else ""

        expander_label = f"<span style='font-size: 24px; font-weight: bold;'>{combatant_name} {hp_emoji} {conditions_emoji} {turn_marker}</span>"

        # Use plain string for the expander label, HTML only inside
        with st.expander(label=f"{combatant_name} {hp_emoji} {conditions_emoji} {turn_marker}", expanded=False):
            st.markdown(expander_label, unsafe_allow_html=True)
            cols = st.columns(3)
            previous_hp = combatant.get('hp', 0)
            combatant['hp'] = cols[0].number_input(f"HP 🧡 (Max: {max_hp})", value=combatant['hp'], min_value=0, max_value=max_hp, key=f"hp_{combatant_name}_{i}")
            combatant['ac'] = cols[1].number_input(f"AC 🛡️", value=combatant['ac'], key=f"ac_{combatant_name}_{i}")
            combatant['initiative'] = cols[2].number_input(f"Initiative 🎲", value=combatant['initiative'], key=f"initiative_{combatant_name}_{i}")

            combatant['concentrating'] = st.checkbox(f"🧘 Concentrating", value=combatant.get('concentrating', False), key=f"concentration_{combatant_name}_{i}")
            combatant['conditions'] = st.multiselect(
                "Conditions",
                options=list(conditions.keys()),
                default=combatant.get('conditions', ['No Condition']),
                key=f"conditions_{combatant_name}_{i}"
            )

            if combatant['concentrating'] and combatant['hp'] != previous_hp:
                st.warning(f"**{combatant_name}** is concentrating. Please roll a concentration check.")

            if st.button(f"Apply changes for {combatant_name}", key=f"apply_{combatant_name}_{i}"):
                idx = st.session_state['combatants'].index(combatant)
                st.session_state['combatants'][idx].update({
                    "hp": combatant['hp'],
                    "ac": combatant['ac'],
                    "initiative": combatant['initiative'],
                    "concentrating": combatant['concentrating'],
                    "conditions": combatant.get('conditions', ["No Condition"]),
                })

            if st.button(f"Remove {combatant_name}", key=f"remove_{combatant_name}_{i}"):
                st.session_state['combatants'].remove(combatant)
                st.experimental_rerun()

if st.button("End Turn") and st.session_state['combatants']:
    st.session_state['current_turn_index'] += 1
    if st.session_state['current_turn_index'] >= len(st.session_state['combatants']):
        st.session_state['current_turn_index'] = 0
        st.session_state['round'] += 1
    st.experimental_rerun()

import streamlit as st
import random

# Displaying the footer section for Attack and Damage application
st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f1f1f1;  /* Light gray background */
            padding: 10px 0;
            box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.1);  /* Shadow for separation */
            z-index: 1000;
            border-top: 2px solid #ccc;  /* Light border on top for separation */
        }
        .footer .stButton button {
            margin: 0 10px;
        }
        .footer .stNumberInput input {
            margin-right: 5px;
        }
        .footer .stSelectbox select {
            margin-right: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Add the Attack header to the footer
st.markdown('<div class="footer">', unsafe_allow_html=True)

st.subheader("Attack ⚔️")  # This is the header for the attack section.

# Create three columns for the footer to display horizontally
col1, col2, col3 = st.columns(3)

# Dropdown to select the combatant
with col1:
    selected_combatant_name = st.selectbox("Select Combatant for Attack", [combatant['name'] for combatant in st.session_state['combatants']])

# Input fields for dice roll and modifier
with col2:
    dice_count = st.number_input("Number of Dice", min_value=1, value=1)
    dice_type = st.number_input("Dice Type", min_value=1, value=6)

with col3:
    modifier = st.number_input("Modifier", value=0)

# Button to generate the damage value
if st.button("Generate Damage"):
    # Random damage roll calculation
    damage_roll = sum(random.randint(1, dice_type) for _ in range(dice_count)) + modifier
    st.session_state['generated_damage'] = damage_roll
    st.write(f"Damage Rolled: {damage_roll}")

# Show the generated damage and allow for manual override
if 'generated_damage' in st.session_state:
    damage_override = st.number_input("Override Damage (if necessary)", value=st.session_state['generated_damage'])
else:
    damage_override = 0

# Apply Damage button
if st.button("Apply Damage"):
    updated_combatants = []
    for combatant in st.session_state['combatants']:
        if combatant['name'] == selected_combatant_name:
            combatant['hp'] = max(0, combatant['hp'] - damage_override)
            combatant_conditions = combatant.get('conditions', [])
            
            # If HP is 0, apply Unconscious condition
            if combatant['hp'] == 0 and "Unconscious" not in combatant_conditions:
                combatant_conditions.append("Unconscious")
            
            combatant['conditions'] = combatant_conditions
            
            # If concentrating, prompt for a concentration check
            if "Concentrating" in combatant_conditions:
                concentration_check = st.radio(f"{combatant['name']} is concentrating! Roll a Concentration Check?", ("Yes", "No"))
                if concentration_check == "Yes":
                    concentration_roll = random.randint(1, 20)
                    st.write(f"Concentration Check Roll: {concentration_roll}")
        updated_combatants.append(combatant)
    
    st.session_state['combatants'] = updated_combatants
    st.success(f"Damage applied to {selected_combatant_name}.")
    
    # Guidance prompt for finalizing the combatant's view
    st.warning(f"Remember to click 'Apply Changes for {selected_combatant_name}' in the combatant interface to finalize updates.")

st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st

# Define the conditions dictionary
conditions = {
    "No Condition": "✅ No active conditions",
    "Bane": "🎲 Subtracts 1d4 from attack rolls and saving throws.",
    "Blessed": "✨ Bonus 1d4 to attack rolls and saving throws.",
    "Blinded": "🙈 Can’t see. Attack rolls against have advantage; own attacks have disadvantage.",
    "Charmed": "💕 Can’t attack charmer; charmer has advantage on social interactions.",
    "Deafened": "👂 Can’t hear. Automatically fails checks requiring hearing.",
    "Frightened": "😨 Disadvantage on checks and attacks while fear source in line of sight.",
    "Grappled": "🤼‍♂️ Speed is 0; ends if grappler is incapacitated or effect ends.",
    "Hasted": "⚡ Doubles speed, +2 AC, advantage on Dex saves, extra action per turn.",
    "Incapacitated": "❌ Can’t take actions or reactions.",
    "Invisible": "👻 Can’t be seen. Attackers have disadvantage; own attacks have advantage.",
    "Paralyzed": "🧍‍♂️ Incapacitated, can’t move or speak. Critical hits if within 5 feet.",
    "Petrified": "🪨 Transformed to stone. Incapacitated and fails Strength/Dex saves.",
    "Poisoned": "☠️ Disadvantage on attack rolls and ability checks.",
    "Prone": "🤸 Can’t move. Disadvantage on attacks; attacks within 5 feet have advantage.",
    "Restrained": "⛓️ Speed is 0; attack rolls have disadvantage; disadvantage on Dex saves.",
    "Shield": "🛡️ +5 AC until the start of the next turn.",
    "Shield of Faith": "🙏 +2 bonus to AC.",
    "Slowed": "🐢 Speed halved; -2 to AC and Dex saves, no reactions.",
    "Stunned": "💫 Can’t move or speak. Fails Strength/Dex saves. Advantage against.",
    "Unconscious": "💤 Incapacitated, can’t move. Critical hits within 5 feet."
}

# Streamlit's sidebar is available natively
st.sidebar.header('Condition Descriptions')

# Display all condition descriptions in the sidebar
for condition, description in conditions.items():
    st.sidebar.markdown(f"**{condition}:** {description}")

import streamlit as st
import random

# Floating Dice Roller Widget outside of any nested UI
with st.container():
    st.markdown("<div style='position: fixed; bottom: 20px; right: 20px; z-index: 1000; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);'>", unsafe_allow_html=True)
    
    st.markdown("### 🎲 Dice Roller")
    
    # Dice type selection
    die_type = st.selectbox("Select a die:", ["d4", "d6", "d8", "d10", "d12", "d20", "d100"], key="die_type_selection")
    
    # Roll the selected die
    if st.button(f"Roll {die_type}", key="roll_die"):
        die_max_value = int(die_type[1:])
        roll_result = random.randint(1, die_max_value)
        st.write(f"**You rolled a {die_type}: {roll_result}**")
    
    # Roll a concentration check
    if st.button("Roll Concentration Check 🎲", key="concentration_check"):
        concentration_roll = random.randint(1, 20)
        st.write(f"**Concentration Check Roll: {concentration_roll}**")
    
    st.markdown("</div>", unsafe_allow_html=True)

















