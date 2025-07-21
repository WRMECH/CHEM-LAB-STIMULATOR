import streamlit as st
from rdkit import Chem
from rdkit.Chem.Draw import MolToImage
import io
import time # Import time for delays

# Suppress RDKit warnings for cleaner output
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

# --- Custom CSS for Dark Theme and Neon Glow ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1a1a2e; /* Deep dark blue/purple background */
        color: #e0e0e0; /* Light gray text */
    }
    .stSelectbox > div > div {
        background-color: #2a2a4a; /* Darker background for select boxes */
        color: #e0e0e0;
        border: 1px solid #4a4a6a;
        box-shadow: 0 0 5px #4a4a6a; /* Subtle glow for select boxes */
    }
    .stButton > button {
        background-color: #00FFFF; /* Default Neon Cyan button */
        color: #1a1a2e; /* Dark text on button */
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF; /* Neon glow */
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #00E0E0;
        box-shadow: 0 0 15px #00FFFF, 0 0 30px #00FFFF;
    }
    /* Specific style for the "Start Titration" button to match screenshot */
    .stButton[data-testid="stButton-titration_button"] > button {
        background-color: #FF00FF; /* Bright Pink */
        box-shadow: 0 0 10px #FF00FF, 0 0 20px #FF00FF;
    }
    .stButton[data-testid="stButton-titration_button"] > button:hover {
        background-color: #E000E0;
        box-shadow: 0 0 15px #FF00FF, 0 0 30px #FF00FF;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #00FFFF; /* Neon Cyan for headers */
        text-shadow: 0 0 5px #00FFFF; /* Subtle glow for headers */
    }
    .stMarkdown {
        color: #e0e0e0; /* Ensure markdown text is readable */
    }
    /* Style for the RDKit image container to ensure white background */
    .stImage > img {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.3); /* Subtle white glow for images */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper function for glowing style
def get_glowing_style(color):
    # A more pronounced glow effect with border and shadow
    return f"background-color:{color}; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid {color}; box-shadow: 0 0 25px {color}, 0 0 40px {color} inset;"

# --- Chemical Definitions ---
class Chemical:
  def __init__(self, name, formula, smiles, color="lightblue", state="liquid", is_indicator=False):
      self.name = name
      self.formula = formula
      self.smiles = smiles # SMILES string for RDKit
      self.color = color
      self.state = state
      self.is_indicator = is_indicator
      self.mol = Chem.MolFromSmiles(smiles) if smiles else None

  def get_image(self):
      """Generates an RDKit image of the chemical structure."""
      if self.mol:
          img = MolToImage(self.mol, size=(200, 200))
          # Convert PIL Image to bytes for Streamlit
          buf = io.BytesIO()
          img.save(buf, format="PNG")
          return buf.getvalue()
      return None

  def __str__(self):
      return f"{self.name} ({self.formula})"

# Pre-defined chemicals with vibrant "neon" colors
CHEMICALS = [
  Chemical("Water", "H2O", "O", color="#00FFFF"), # Electric Blue
  Chemical("Hydrochloric Acid", "HCl", "Cl", color="#FF00FF"), # Bright Pink
  Chemical("Sodium Hydroxide", "NaOH", "O[Na]", color="#00FF00"), # Lime Green
  Chemical("Sodium Chloride", "NaCl", "[Na]Cl", color="#808080"), # Gray (neutral product)
  Chemical("Hydrogen Gas", "H2", "[H][H]", color="#FFFF00", state="gas"), # Electric Yellow
  Chemical("Oxygen Gas", "O2", "O=O", color="#FFA500", state="gas"), # Vibrant Orange
  Chemical("Iron", "Fe", "[Fe]", color="#8A2BE2", state="solid"), # Blue Violet
  Chemical("Iron(II) Chloride", "FeCl2", "Cl[Fe]Cl", color="#4B0082"), # Indigo
  Chemical("Carbon Dioxide", "CO2", "O=C=O", color="#F0F8FF", state="gas"), # Alice Blue (light gas)
  Chemical("Methane", "CH4", "C", color="#7FFF00", state="gas"), # Chartreuse
  Chemical("Zinc", "Zn", "[Zn]", color="#00CED1", state="solid"), # Dark Turquoise
  Chemical("Zinc Chloride", "ZnCl2", "Cl[Zn]Cl", color="#00FFFF"), # Electric Blue
  Chemical("Lead Nitrate", "Pb(NO3)2", "O=[N+]([O-])[O-].[Pb]", color="#FFD700"), # Gold
  Chemical("Potassium Iodide", "KI", "[K]I", color="#FF69B4"), # Hot Pink
  Chemical("Lead Iodide", "PbI2", "I[Pb]I", color="#FFFF00", state="solid"), # Yellow (for precipitate)
  Chemical("Potassium Nitrate", "KNO3", "O=[N+]([O-])[O-].[K]", color="#808080"), # Gray (neutral product)
  Chemical("Copper", "Cu", "[Cu]", color="#FF4500", state="solid"), # OrangeRed
  Chemical("Silver Nitrate", "AgNO3", "O=[N+]([O-])[O-].[Ag]", color="#C0C0C0"), # Silver (neutral)
  Chemical("Silver", "Ag", "[Ag]", color="#E0E0E0", state="solid"), # Light Silver (neutral product)
  Chemical("Copper Nitrate", "Cu(NO3)2", "O=[N+]([O-])[O-].[Cu]", color="#00BFFF"), # Deep Sky Blue
  # New chemicals for titration
  Chemical("Sulfuric Acid", "H2SO4", "OS(O)(=O)=O", color="#FF00FF"), # Bright Pink
  Chemical("Potassium Hydroxide", "KOH", "O[K]", color="#00FF00"), # Lime Green
  Chemical("Phenolphthalein", "C20H14O4", "OC1=CC=C(C=C1)C(C1=CC=CC=C1)(C1=CC=C(O)C=C1)C(=O)O", color="#FFFFFF", is_indicator=True), # White (colorless)
  Chemical("Methyl Orange", "C14H14N3NaO3S", "CN(C)C1=CC=C(C=C1)N=NC1=CC=C(S(=O)(=O)[O-])C=C1.[Na+]", color="#FF0000", is_indicator=True), # Red (acidic)
]

# Create a dictionary for easy lookup
CHEMICAL_MAP = {chem.name: chem for chem in CHEMICALS}

# Separate lists for easy selection in UI
ACIDS = [c for c in CHEMICALS if "Acid" in c.name and not c.is_indicator]
BASES = [c for c in CHEMICALS if "Hydroxide" in c.name and not c.is_indicator]
INDICATORS = [c for c in CHEMICALS if c.is_indicator]

# --- Reaction Logic ---
def simulate_reaction(chem1: Chemical, chem2: Chemical):
  """
  Simulates a chemical reaction between two selected chemicals.
  Returns a list of product chemicals and a log of the reaction.
  """
  products = []
  log = []
  reaction_occurred = False

  # Acid-Base Neutralization: HCl + NaOH -> NaCl + H2O
  if (chem1.name == "Hydrochloric Acid" and chem2.name == "Sodium Hydroxide") or \
     (chem2.name == "Hydrochloric Acid" and chem1.name == "Sodium Hydroxide"):
      products.append(CHEMICAL_MAP["Sodium Chloride"])
      products.append(CHEMICAL_MAP["Water"])
      log.append(f"**Reaction:** {chem1.formula} + {chem2.formula} → {CHEMICAL_MAP['Sodium Chloride'].formula} + {CHEMICAL_MAP['Water'].formula}")
      log.append("This is an acid-base neutralization reaction, forming salt and water.")
      reaction_occurred = True

  # Synthesis/Combustion: H2 + O2 -> H2O
  elif (chem1.name == "Hydrogen Gas" and chem2.name == "Oxygen Gas") or \
       (chem2.name == "Hydrogen Gas" and chem1.name == "Oxygen Gas"):
      products.append(CHEMICAL_MAP["Water"])
      log.append(f"**Reaction:** {CHEMICAL_MAP['Hydrogen Gas'].formula} + {CHEMICAL_MAP['Oxygen Gas'].formula} → {CHEMICAL_MAP['Water'].formula}")
      log.append("Hydrogen and Oxygen combine to form Water. This is a synthesis reaction, often exothermic.")
      reaction_occurred = True

    # Metal-Acid Reaction: Zn + HCl -> ZnCl2 + H2
  elif (chem1.name == "Zinc" and chem2.name == "Hydrochloric Acid") or \
       (chem2.name == "Zinc" and chem1.name == "Hydrochloric Acid"):
      products.append(CHEMICAL_MAP["Zinc Chloride"])
      products.append(CHEMICAL_MAP["Hydrogen Gas"])
      log.append(f"**Reaction:** {CHEMICAL_MAP['Zinc'].formula} + {CHEMICAL_MAP['Hydrochloric Acid'].formula} → {CHEMICAL_MAP['Zinc Chloride'].formula} + {CHEMICAL_MAP['Hydrogen Gas'].formula}")
      log.append("This is a single displacement reaction. Zinc displaces hydrogen from hydrochloric acid, producing hydrogen gas (effervescence).")
      reaction_occurred = True

    # Precipitation Reaction: Pb(NO3)2 + KI -> PbI2(s) + KNO3
  elif (chem1.name == "Lead Nitrate" and chem2.name == "Potassium Iodide") or \
       (chem2.name == "Lead Nitrate" and chem1.name == "Potassium Iodide"):
      products.append(CHEMICAL_MAP["Lead Iodide"])
      products.append(CHEMICAL_MAP["Potassium Nitrate"])
      log.append(f"**Reaction:** {CHEMICAL_MAP['Lead Nitrate'].formula} + {CHEMICAL_MAP['Potassium Iodide'].formula} → {CHEMICAL_MAP['Lead Iodide'].formula}(s) + {CHEMICAL_MAP['Potassium Nitrate'].formula}")
      log.append("This is a double displacement (precipitation) reaction. A yellow precipitate of Lead Iodide is formed.")
      reaction_occurred = True

    # Single Displacement/Redox: Cu + AgNO3 -> Cu(NO3)2 + Ag
  elif (chem1.name == "Copper" and chem2.name == "Silver Nitrate") or \
       (chem2.name == "Copper" and chem1.name == "Silver Nitrate"):
      products.append(CHEMICAL_MAP["Copper Nitrate"])
      products.append(CHEMICAL_MAP["Silver"])
      log.append(f"**Reaction:** {CHEMICAL_MAP['Copper'].formula} + {CHEMICAL_MAP['Silver Nitrate'].formula} → {CHEMICAL_MAP['Copper Nitrate'].formula} + {CHEMICAL_MAP['Silver'].formula}")
      log.append("This is a single displacement reaction. Copper displaces silver from silver nitrate. Silver metal is deposited, and the solution turns blue due to Copper Nitrate.")
      reaction_occurred = True

    # Combustion: CH4 + O2 -> CO2 + H2O
  elif (chem1.name == "Methane" and chem2.name == "Oxygen Gas") or \
       (chem2.name == "Methane" and chem1.name == "Oxygen Gas"):
      products.append(CHEMICAL_MAP["Carbon Dioxide"])
      products.append(CHEMICAL_MAP["Water"])
      log.append(f"**Reaction:** {CHEMICAL_MAP['Methane'].formula} + {CHEMICAL_MAP['Oxygen Gas'].formula} → {CHEMICAL_MAP['Carbon Dioxide'].formula} + {CHEMICAL_MAP['Water'].formula}")
      log.append("This is a combustion reaction. Methane burns in oxygen to produce carbon dioxide and water.")
      reaction_occurred = True

  # Single Displacement: Fe + HCl -> FeCl2 + H2
  elif (chem1.name == "Iron" and chem2.name == "Hydrochloric Acid") or \
       (chem2.name == "Iron" and chem1.name == "Hydrochloric Acid"):
      products.append(CHEMICAL_MAP["Iron(II) Chloride"])
      products.append(CHEMICAL_MAP["Hydrogen Gas"])
      log.append(f"**Reaction:** {CHEMICAL_MAP['Iron'].formula} + {CHEMICAL_MAP['Hydrochloric Acid'].formula} → {CHEMICAL_MAP['Iron(II) Chloride'].formula} + {CHEMICAL_MAP['Hydrogen Gas'].formula}")
      log.append("Iron reacts with Hydrochloric Acid in a single displacement reaction, producing hydrogen gas.")
      reaction_occurred = True

  # No specific reaction defined
  if not reaction_occurred:
      products.extend([chem1, chem2]) # They just remain mixed
      log.append(f"**Observation:** No specific chemical reaction observed between {chem1.name} and {chem2.name}.")
      log.append("They appear to simply mix together.")

  return products, log

def simulate_titration_experiment(acid: Chemical, base: Chemical, indicator: Chemical):
    log = []
    initial_color = ""
    final_color = ""
    
    # Determine initial and final colors based on indicator
    if indicator.name == "Phenolphthalein":
        initial_color = "#FFFFFF" # Colorless (represented as white for the box)
        final_color = "#FF69B4" # Hot Pink (as in screenshot)
        log.append(f"**Titration Setup:** {acid.name} ({acid.formula}) with {indicator.name} added. Solution is initially colorless.")
    elif indicator.name == "Methyl Orange":
        initial_color = "#FF0000" # Red (acidic)
        final_color = "#FFFF00" # Yellow (basic)
        log.append(f"**Titration Setup:** {acid.name} ({acid.formula}) with {indicator.name} added. Solution is initially red.")
    else:
        initial_color = "#00FFFF" # Default for unknown indicator
        final_color = "#00FFFF"
        log.append(f"**Titration Setup:** {acid.name} ({acid.formula}) with {indicator.name} added. Initial color is {initial_color}.")

    log.append(f"Titrating with {base.name} ({base.formula}).")

    return log, initial_color, final_color


# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Virtual Chemistry Lab", initial_sidebar_state="expanded")

st.title("🧪 Virtual Chemistry Lab Simulator")
st.markdown("Mix two chemicals and observe the virtual reaction!")

st.markdown("---")

# --- General Mixing Section ---
st.header("General Chemical Mixing")
col1, col2 = st.columns(2)

with col1:
  st.subheader("Chemical A")
  chem_a_name = st.selectbox("Select Chemical A", list(CHEMICAL_MAP.keys()), key="chem_a")
  selected_chem_a = CHEMICAL_MAP[chem_a_name]
  st.write(f"**Name:** {selected_chem_a.name}")
  st.write(f"**Formula:** {selected_chem_a.formula}")
  st.write(f"**State:** {selected_chem_a.state.capitalize()}")
  if selected_chem_a.get_image():
      st.image(selected_chem_a.get_image(), caption=f"{selected_chem_a.name} Structure")
  else:
      st.info("No structure image available for this chemical.")

with col2:
  st.subheader("Chemical B")
  chem_b_name = st.selectbox("Select Chemical B", list(CHEMICAL_MAP.keys()), key="chem_b")
  selected_chem_b = CHEMICAL_MAP[chem_b_name]
  st.write(f"**Name:** {selected_chem_b.name}")
  st.write(f"**Formula:** {selected_chem_b.formula}")
  st.write(f"**State:** {selected_chem_b.state.capitalize()}")
  if selected_chem_b.get_image():
      st.image(selected_chem_b.get_image(), caption=f"{selected_chem_b.name} Structure")
  else:
      st.info("No structure image available for this chemical.")

if st.button("Mix Chemicals", help="Click to simulate the reaction", key="mix_button"):
  st.subheader("🔬 Reaction Simulation")

  # Placeholder for animation messages
  animation_placeholder = st.empty()
  progress_bar_placeholder = st.empty()
  reacting_chemicals_placeholder = st.empty() # Placeholder for the "before reaction" chemicals that will dynamically update

  # Display "Before Reaction" state
  animation_placeholder.markdown("#### Before Reaction:")
  with reacting_chemicals_placeholder.container():
      before_cols = st.columns(2)
      with before_cols[0]:
          st.markdown(f"<div style='{get_glowing_style(selected_chem_a.color)}'>", unsafe_allow_html=True)
          st.markdown(f"### {selected_chem_a.name}")
          st.markdown(f"*{selected_chem_a.state.capitalize()}*")
          st.markdown("</div>", unsafe_allow_html=True)
      with before_cols[1]:
          st.markdown(f"<div style='{get_glowing_style(selected_chem_b.color)}'>", unsafe_allow_html=True)
          st.markdown(f"### {selected_chem_b.name}")
          st.markdown(f"*{selected_chem_b.state.capitalize()}*")
          st.markdown("</div>", unsafe_allow_html=True)

  time.sleep(1) # Pause for effect

  # Simulate mixing
  animation_placeholder.markdown("#### Mixing Chemicals...")
  time.sleep(1)

  # Simulate reaction progress with visual "glow"
  animation_placeholder.markdown("#### Reaction in progress...")
  progress_bar = progress_bar_placeholder.progress(0)
  # Cycle through a few neon colors for the reaction animation
  reaction_glow_colors = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF00", "#FF4500"]
  
  for percent_complete in range(100):
      time.sleep(0.02) # Simulate reaction time
      progress_bar.progress(percent_complete + 1)

      # Update chemical box colors to simulate glow/reaction
      current_color_index = (percent_complete // 20) % len(reaction_glow_colors) # Cycle every 20%
      current_glow_color = reaction_glow_colors[current_color_index]

      with reacting_chemicals_placeholder.container(): # Update the same placeholder
          cols_during_reaction = st.columns(2)
          with cols_during_reaction[0]:
              st.markdown(f"<div style='{get_glowing_style(current_glow_color)}'>", unsafe_allow_html=True)
              st.markdown(f"### {selected_chem_a.name}")
              st.markdown(f"*{selected_chem_a.state.capitalize()}*")
              st.markdown("</div>", unsafe_allow_html=True)
          with cols_during_reaction[1]:
              st.markdown(f"<div style='{get_glowing_style(current_glow_color)}'>", unsafe_allow_html=True)
              st.markdown(f"### {selected_chem_b.name}")
              st.markdown(f"*{selected_chem_b.state.capitalize()}*")
              st.markdown("</div>", unsafe_allow_html=True)

  progress_bar_placeholder.empty() # Clear the progress bar
  reacting_chemicals_placeholder.empty() # Clear the reacting chemicals display

  animation_placeholder.markdown("#### Reaction Complete!")
  time.sleep(0.5)

  # Simulate and display "After Reaction" state
  st.markdown("<br>", unsafe_allow_html=True) # Add some space
  st.markdown("#### After Reaction:")
  products, reaction_log = simulate_reaction(selected_chem_a, selected_chem_b)

  if products:
      product_cols = st.columns(len(products))
      for i, product in enumerate(products):
          with product_cols[i]:
              st.markdown(f"<div style='{get_glowing_style(product.color)}'>", unsafe_allow_html=True)
              st.markdown(f"### {product.name}")
              st.markdown(f"*{product.state.capitalize()}*")
              st.markdown("</div>", unsafe_allow_html=True)
              if product.get_image():
                  st.image(product.get_image(), caption=f"{product.name} Structure")
              else:
                  st.info("No structure image available.")
  else:
      st.warning("No products formed or recognized in this reaction.")

  st.markdown("---")

  # Reaction Log
  st.subheader("📝 Reaction Log")
  for entry in reaction_log:
      st.markdown(f"- {entry}")

  st.success("Reaction simulation complete!")

st.markdown("---")

# --- Titration Experiment Section ---
st.header("🧪 Titration Experiment")
st.markdown("Simulate an acid-base titration with an indicator.")

titration_col1, titration_col2, titration_col3 = st.columns(3)

with titration_col1:
    selected_acid_name = st.selectbox("Select Acid (Analyte)", [a.name for a in ACIDS], key="titration_acid")
    selected_acid = CHEMICAL_MAP[selected_acid_name]
    st.write(f"**Formula:** {selected_acid.formula}")

with titration_col2:
    selected_base_name = st.selectbox("Select Base (Titrant)", [b.name for b in BASES], key="titration_base")
    selected_base = CHEMICAL_MAP[selected_base_name]
    st.write(f"**Formula:** {selected_base.formula}")

with titration_col3:
    selected_indicator_name = st.selectbox("Select Indicator", [i.name for i in INDICATORS], key="titration_indicator")
    selected_indicator = CHEMICAL_MAP[selected_indicator_name]
    st.write(f"**Formula:** {selected_indicator.formula}")

if st.button("Start Titration", help="Simulate the titration process", key="titration_button"):
    st.subheader("🔬 Titration Simulation")

    titration_log, initial_color, final_color = simulate_titration_experiment(selected_acid, selected_base, selected_indicator)

    titration_animation_placeholder = st.empty()
    titration_progress_bar_placeholder = st.empty()
    titration_solution_placeholder = st.empty() # Placeholder for the solution box

    # Initial state
    titration_animation_placeholder.markdown("#### Initial Solution:")
    with titration_solution_placeholder.container():
        st.markdown(f"<div style='{get_glowing_style(initial_color)}; height: 150px; display: flex; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
        st.markdown(f"### {selected_acid.name} + {selected_indicator.name}")
        st.markdown("</div>", unsafe_allow_html=True)
    time.sleep(1)

    # Titration in progress
    titration_animation_placeholder.markdown("#### Adding Titrant (Drop by Drop)...")
    progress_bar = titration_progress_bar_placeholder.progress(0)
    
    # Simulate drops and color change
    # Define a set of transition colors for a more dynamic effect
    titration_transition_colors = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF00", "#FF4500"] 
    
    for percent_complete in range(100):
        time.sleep(0.03) # Simulate drop addition
        progress_bar.progress(percent_complete + 1)

        # Dynamic color change based on progress
        current_solution_color = initial_color
        if percent_complete >= 70 and percent_complete < 90: # Transition phase
            # Cycle through transition colors
            transition_index = (percent_complete - 70) % len(titration_transition_colors)
            current_solution_color = titration_transition_colors[transition_index]
        elif percent_complete >= 90: # Equivalence point reached/passed
            current_solution_color = final_color

        with titration_solution_placeholder.container():
            st.markdown(f"<div style='{get_glowing_style(current_solution_color)}; height: 150px; display: flex; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
            st.markdown(f"### {selected_acid.name} + {selected_indicator.name}")
            st.markdown("</div>", unsafe_allow_html=True)

    titration_progress_bar_placeholder.empty()
    titration_animation_placeholder.markdown("#### Titration Complete!")
    time.sleep(0.5)

    # Final state
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Final Solution:")
    with titration_solution_placeholder.container(): # Update with final color
        st.markdown(f"<div style='{get_glowing_style(final_color)}; height: 150px; display: flex; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
        st.markdown(f"### {selected_acid.name} + {selected_indicator.name} (Neutralized)")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📝 Titration Log")
    for entry in titration_log:
        st.markdown(f"- {entry}")
    st.markdown(f"- **Observation:** The solution changed color from {initial_color} to {final_color}, indicating the equivalence point was reached.")
    st.success("Titration simulation complete!")

st.markdown("---")
st.markdown("### How it works:")
st.markdown("""
This simulator uses a simplified set of predefined chemical reactions and titration principles.
When you select and mix two chemicals, the system checks for known reactions.
For titration, it simulates the addition of a base to an acid with an indicator, showing the expected color change.
Molecular structures are visualized using the RDKit library.

**Note on 3D Animations:**
While this simulator enhances visual feedback with dynamic color changes and a "glow" effect,
true interactive 3D molecular animations (like rotating models) are beyond the direct capabilities
of Streamlit using only Python. Such features typically require JavaScript-based 3D libraries
(e.g., Three.js, Babylon.js) or pre-rendered 3D assets (like GIFs or videos) which would need
to be generated by external tools.
""")
