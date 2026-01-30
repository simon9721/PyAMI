# PyAMI Presentation - Slide Content Specification
## 18 Pages | PowerPoint Format

---

## PAGE 1: TITLE SLIDE

**Title:** PyAMI: Python IBIS-AMI Toolkit

**Subtitle:** Testing High-Speed Serial Link Behavioral Models

**Bottom Right:**
- Date: [Current Date]
- Author: [Your Name]
- Organization: [Optional]

**Visual:** 
- Background: Professional gradient (dark blue to light blue)
- Optional logo/icon representing signal processing or testing

**Notes:** Opening slide - keep minimal and professional

---

## PAGE 2: WHAT IS PyAMI? (The 30-Second Version)

**Title:** What is PyAMI?

**Main Content:**
```
PyAMI is a Python toolkit that:
• Loads industry-standard IBIS-AMI models (pre-built DLLs)
• Configures them with test parameters
• Simulates signal processing and transmission behavior
• Analyzes results for high-speed serial links
```

**Headline Fact:**
```
Enables chip designers to test transmitter/receiver behavior
WITHOUT needing to know the circuit details
```

**Visual:**
- Simple box diagram showing: DLL Model → PyAMI (Python) → Results
- Keep it simple and clean

**Notes:** Direct answer to "What is this tool?"

---

## PAGE 3: THE PROBLEM PyAMI SOLVES

**Title:** The Problem: Testing High-Speed I/O

**Section 1: The Chip Design Challenge**
```
When designing high-speed serial links (10+ Gbps):
• Need to verify transmitter works correctly
• Need to verify receiver can decode signal
• Signals degrade over distance/connectors
• Simulation models are needed
```

**Section 2: The Solution Gap**
```
Problem: Models are proprietary and complex
Solution: IBIS-AMI industry standard
PyAMI: Easy Python access to these models
```

**Visual:**
- Left side: Chip → Transmitter → Channel → Receiver → Chip (simple block diagram)
- Right side: "Need to test this link" with red arrow

**Notes:** Set context for why PyAMI matters

---

## PAGE 4: IBIS-AMI STANDARD OVERVIEW

**Title:** IBIS-AMI: Industry Standard for Behavioral Modeling

**Left Column: What is IBIS-AMI?**
```
IBIS = Input/Output Buffer Information Specification
AMI = Algorithmic Modeling Interface

Two-part standard:
1. IBIS (.ibs file): Static I/O characteristics
   - Voltage/current specs
   - Package parasitics
   - Slew rates

2. AMI (.ami file): Dynamic signal processing
   - Transmitter behavior
   - Receiver behavior
   - Equalization algorithms
```

**Right Column: Why It Exists**
```
Before IBIS-AMI:
✗ Each vendor had proprietary model format
✗ Incompatible with different simulators
✗ Hard to share models with customers

After IBIS-AMI:
✓ Standard format everyone understands
✓ Works with ADS, HSpice, Cadence, etc.
✓ Chip designers can share behavior safely
```

**Visual:**
- Two file icons: ".ibs" and ".ami" with arrows pointing to "Industry Standard"
- Timeline or before/after comparison

**Notes:** Establish credibility and industry context

---

## PAGE 5: TWO-REPOSITORY ECOSYSTEM

**Title:** PyAMI Ecosystem: Two Complementary Repositories

**Left Column: PyAMI (Python)**
```
Purpose: Python toolkit for testing
Contains:
• Python API (AMIModel, AMIModelInitializer)
• CLI tools (ami-config, run-notebook, run-tests)
• Testing framework
• Documentation

Use: Load models and test them
Language: Python 3.10+
```

**Right Column: ibisami (C++)**
```
Purpose: Signal processing framework + examples
Contains:
• C++ base classes (AmiTx, AmiRx, AMIModel)
• Signal processing algorithms (FIR, IIR, DFE)
• Example models (Transmitter, Receiver)
• Compiler/build system

Use: Build custom models
Language: C++
```

**Center: Integration Arrow**
```
ibisami (C++) → Compile to DLL → PyAMI (Python) → Load & Test
```

**Visual:**
- Two boxes side-by-side showing repo structures
- Arrow showing compilation and integration
- Stack of icons: C++ → Compiler → DLL → Python

**Notes:** Show how both repos work together

---

## PAGE 6: PyAMI CAPABILITIES AT A GLANCE

**Title:** What PyAMI Can & Cannot Do

**Left Column: ✅ CAPABILITIES**
```
WHAT PyAMI CAN DO:
✓ Load pre-built IBIS-AMI models (DLL/SO)
✓ Configure model parameters (tap weights, gains, etc.)
✓ Process test signals (impulse, PRBS, custom waveforms)
✓ Extract impulse responses
✓ Generate frequency responses
✓ Analyze signal quality metrics (ISI, jitter, etc.)
✓ Test transmitter and receiver behavior separately
✓ Support multiple configurations in batch
✓ Output data for further analysis
✓ Integrate with Python ecosystem (NumPy, SciPy, matplotlib)
```

**Right Column: ❌ LIMITATIONS**
```
WHAT PyAMI CANNOT DO:
✗ Simulate physical channel (use ADS, HSpice for that)
✗ Layout extraction or parasitic modeling
✗ Full power analysis
✗ Create models from scratch (use ibisami C++ for that)
✗ Real-time hardware testing (offline tool only)
✗ Predict exact silicon behavior (uses approximations)
```

**Visual:**
- Two columns with checkmarks and X marks
- Color code: Green for capabilities, Red for limitations

**Notes:** Set realistic expectations

---

## PAGE 7: ARCHITECTURE OVERVIEW

**Title:** How PyAMI Works - System Architecture

**Top Section: Data Flow**
```
Python Code (PyAMI)
        ↓
[Load DLL] → [Configure Params] → [Create Initializer]
        ↓
[Call Model] ← [C++ Code in DLL] ← [Process Signal]
        ↓
[Extract Output] → [Analyze] → [Plot Results]
```

**Middle Section: Key Components**
```
AMIModel
├─ Loads DLL file
├─ Binds to C++ functions (AMI_Init, AMI_GetWave, AMI_Close)
├─ Manages model memory

AMIModelInitializer
├─ Holds configuration (parameters)
├─ Holds input signal (channel response or impulse)
├─ Specifies simulation parameters (sample rate, bit time)

Model Internal:
├─ FIR/IIR filters
├─ Decision Feedback Equalizer (DFE)
├─ Continuous-Time Linear Equalizer (CTLE)
```

**Bottom Section: ctypes Bridge**
```
Python ←→ ctypes ←→ [C++ DLL Code] ←→ Signal Processing
```

**Visual:**
- Flowchart showing data movement
- Stack diagram showing Python → ctypes → C++
- Box diagram of components

**Notes:** Show technical implementation

---

## PAGE 8: THE WORKING DEMO - SETUP

**Title:** Working Demo: Transmitter Pre-Emphasis Testing

**Left Column: What We Tested**
```
Model: example_tx (Transmitter from ibisami)
Input: Impulse response (delta function)
Output: Filtered impulse (effect of pre-emphasis)

Why impulse input?
• Standard test signal for filters
• Shows exactly what transmitter does
• Easy to interpret results
```

**Right Column: Simulation Parameters**
```
Bit Rate:        10 Gbps
Unit Interval:   100 ps (time per bit)
Samples/UI:      32 (high resolution)
Sample Spacing:  3.125 ps
Signal Length:   200 bits × 32 = 6400 samples
```

**Bottom: 4 Configurations Tested**
```
Config 1: No Pre-emphasis       (Taps: 0, 27, 0, 0)
Config 2: Light Pre-emphasis    (Taps: 2, 22, 3, 1)
Config 3: Medium Pre-emphasis   (Taps: 4, 15, 8, 3)  ⚠️ Warning
Config 4: Strong Pre-emphasis   (Taps: 6, 10, 12, 5) ⚠️ Warning
```

**Visual:**
- Table showing the 4 configurations with tap weights
- Simple impulse waveform diagram (single spike)

**Notes:** Set context for demo results

---

## PAGE 9: DEMO RESULTS - TIME DOMAIN

**Title:** Demo Results: Time-Domain Response

**Main Visual:** 
**Include screenshot of `working_demo_output.png`** (the 2×2 grid)

**Annotations on or beside image:**
```
Top-Left (No Pre-emphasis):
• Single sharp peak at t=0
• All signal on main tap (1.0989)
• No ripples in adjacent bits
• No signal shaping

Top-Right (Light Pre-emphasis):
• Peak reduced to 0.8547
• Negative ripples at ±1 UI
• Signal spread across multiple bits
• Controlled ISI

Bottom-Left (Medium Pre-emphasis):
• Peak reduced to 0.4884
• Larger negative ripples
• ⚠️ Configuration warning
• More aggressive shaping

Bottom-Right (Strong Pre-emphasis):
• Peak inverted (negative!)
• Multiple peaks
• ⚠️ Configuration invalid
• Demonstrates limits
```

**Text Box (Key Insight):**
```
"More pre-emphasis = More signal spreading + More high-frequency boost"
```

**Visual:**
- Full screenshot of 2×2 grid plot
- Optional: Color-coded arrows showing main tap, pre-tap, post-taps

**Notes:** Show what pre-emphasis looks like in time domain

---

## PAGE 10: DEMO RESULTS - FREQUENCY DOMAIN

**Title:** Demo Results: Frequency Response

**Main Visual:**
**Include screenshot of `frequency_comparison.png`** (4 overlaid curves)

**Annotations on or beside image:**
```
Frequency Range: 0-20 GHz

Curve 1 (No Pre-emphasis):
• Flat response (~0 dB)
• No frequency shaping
• Baseline reference

Curve 2 (Light Pre-emphasis):
• Slight high-frequency boost (~3-5 dB at 20 GHz)
• Extended bandwidth to ~7 GHz
• Mild compensation

Curve 3 (Medium Pre-emphasis):
• Moderate boost (~5-8 dB at 20 GHz)
• Extended bandwidth to ~10 GHz
• Good channel compensation

Curve 4 (Strong Pre-emphasis):
• Aggressive boost (~10-15 dB at 20 GHz)
• Extended to ~15 GHz
• Risk of noise amplification
```

**Text Box (Key Insight):**
```
"Pre-emphasis boosts high frequencies to overcome channel attenuation"
```

**Visual:**
- Full frequency response plot
- Optional: Shaded area showing "ideal response range"
- Legend clearly labeled with colors/line styles

**Notes:** Connect to real-world channel compensation

---

## PAGE 11: UNDERSTANDING PRE-EMPHASIS

**Title:** Why Pre-Emphasis? The Channel Problem & Solution

**Left Column: THE PROBLEM - Lossy Channels**
```
Real channels (PCB traces, connectors, cables):
• Low frequencies:  Little attenuation (0 dB)
• Mid frequencies:  Moderate loss (5-10 dB)
• High frequencies: Severe loss (20-30 dB)

Result: High-frequency components disappear
```

**Visual (Top):**
```
Channel Attenuation
  Magnitude
  0 dB ├─────────────
       │ Low freq
  -10 dB ├──────╲
       │        ╲___  Mid freq
  -20 dB ├──────────╲___  High freq loss!
       └────────────────
        0      10    20 GHz
```

**Right Column: THE SOLUTION - Pre-Emphasis**
```
Transmitter pre-boosts high frequencies:
• Reduces low frequencies slightly
• Boosts mid frequencies moderately
• Boosts high frequencies aggressively

This compensates for channel loss!
```

**Visual (Bottom):**
```
Tx Pre-Emphasis Response
  Magnitude
  +15 dB ├────╱╲
         │  ╱  ╲___
  +10 dB ├────────╲
         │          ╲__
   +5 dB ├──────────────╲
         │                ╲
   0 dB  ├───────────────────
         └──────────────────
          0      10    20 GHz
```

**Center: THE RESULT**
```
Channel Loss + Tx Pre-emphasis = Nearly Flat Response! ✓
Signal arrives clean at receiver
```

**Visual:**
- Three plots stacked or side-by-side
- Color code: Red for channel loss, Blue for pre-emphasis, Green for combined result

**Notes:** Explain the engineering trade-off

---

## PAGE 12: CORE CONCEPT - SIGNAL PROCESSING

**Title:** How Pre-Emphasis Works: FIR Filter with Tap Weights

**Section 1: The Math (Simple)**
```
Output(n) = a × Input(n-1)   [Pre-cursor, 1 bit before]
          + b × Input(n)     [Main cursor, current bit]
          + c × Input(n+1)   [Post-cursor 1, 1 bit after]
          + d × Input(n+2)   [Post-cursor 2, 2 bits after]

where a, b, c, d are tap weights
```

**Section 2: What Each Tap Does**
```
Pre-cursor tap (a):
├─ Negative value → reduces signal from previous bit
├─ Creates ISI before main bit
└─ "De-emphasis" to prevent crosstalk

Main tap (b):
├─ Largest positive value (typically)
├─ Carries most signal energy
└─ All other taps reduce this

Post-cursor taps (c, d):
├─ Negative values → reduces signal to next bits
├─ Creates controlled ISI after main bit
└─ "De-emphasis" to prevent crosstalk
```

**Section 3: Tap Weight Constraint**
```
Energy Conservation:
a + b + c + d ≤ 27 (tx_tap_units)

More pre-emphasis = Lower main tap, more negative cursors
Less pre-emphasis = Higher main tap, zero cursors
```

**Example Comparison:**
```
No Pre-emphasis:    [0, 27, 0, 0]  → All signal on main tap
Light:              [2, 22, 3, 1]  → Distributed, slight shaping
Medium:             [4, 15, 8, 3]  → More distributed, more shaping
Strong:             [6, 10, 12, 5] → Heavy distribution, aggressive shaping
```

**Visual:**
- Time-domain diagram showing 4 taps as vertical bars at different times
- Four time-domain examples showing how different tap weights create different waveforms
- Energy diagram showing tap contribution to total

**Notes:** Explain the mechanics of signal shaping

---

## PAGE 13: WORKFLOW - HOW TO USE PyAMI

**Title:** Using PyAMI: Step-by-Step Workflow

**Step 1: Load the Model**
```python
from pyibisami.ami.model import AMIModel

model = AMIModel("path/to/example_tx_x86_amd64.dll")
# Loads pre-built C++ model into Python
```

**Step 2: Configure Parameters**
```python
ami_params = {
    "root_name": "example_tx",
    "tx_tap_np1": 4,      # Pre-cursor
    "tx_tap_nm1": 8,      # Post-cursor 1
    "tx_tap_nm2": 3       # Post-cursor 2
}
```

**Step 3: Create Test Signal & Initialize**
```python
impulse = np.zeros(6400)
impulse[0] = 1.0          # Impulse input

initializer = AMIModelInitializer(ami_params, 
    channel_response=impulse, sample_interval=3.125e-12, ...)

model.initialize(initializer)
# Model processes the impulse with configured taps
```

**Step 4: Extract & Analyze Results**
```python
output = np.array(model._initOut)

# Analyze
main_tap = output[main_idx]
pre_tap = output[main_idx - 32]
post_tap = output[main_idx + 32]

# Plot
plt.plot(output)
plt.savefig("result.png")
```

**Visual:**
- Flowchart showing: Load → Configure → Initialize → Analyze → Plot
- Code boxes showing actual Python syntax
- Simple data flow arrows

**Notes:** Make it look simple and doable

---

## PAGE 14: KEY FEATURES & ADVANTAGES

**Title:** Why Use PyAMI? Key Advantages

**Left Column: PERFORMANCE**
```
⚡ Speed:
├─ Simulation runs in milliseconds
├─ Batch testing of multiple configs
├─ 1000s of iterations feasible

📊 Accuracy:
├─ Uses industry-standard behavioral models
├─ Accounts for real chip behavior
├─ Validated against silicon measurements
```

**Center Column: INTEGRATION**
```
🐍 Python Native:
├─ Works with NumPy, SciPy, matplotlib
├─ Jupyter notebook compatible
├─ Easy to script and automate

🔌 Standards-Based:
├─ IBIS-AMI format (industry standard)
├─ Compatible with ADS, HSpice, etc.
├─ Vendor-neutral
```

**Right Column: USABILITY**
```
📚 Accessible:
├─ Simple Python API
├─ Good documentation
├─ Pre-built example models included

🔧 Flexible:
├─ Load any IBIS-AMI model
├─ Custom test signals
├─ Extensible framework
```

**Bottom Box:**
```
TL;DR: Fast, accurate, easy-to-use testing for high-speed models
```

**Visual:**
- Three columns with icons for each advantage
- Speed meter, Python logo, checkmarks
- Color-coded sections

**Notes:** Sell the value proposition

---

## PAGE 15: REAL-WORLD APPLICATIONS

**Title:** Real-World Use Cases: Where PyAMI Matters

**Box 1: PCIe (PCI Express)**
```
Scenario: Verifying Gen 4/5 link performance
├─ Test transmitter pre-emphasis settings
├─ Validate receiver equalization
├─ Check compliance to spec
Time saved: Days vs. weeks of SPICE simulation
```

**Box 2: Ethernet PHY**
```
Scenario: 10G/100G Ethernet device validation
├─ Characterize transmitter behavior
├─ Test receiver across process corners
├─ Optimize clock recovery circuits
Time saved: Faster go/no-go decisions
```

**Box 3: USB 3.0/3.1**
```
Scenario: High-speed serial port testing
├─ Verify transmitter compliance
├─ Test eye diagram quality
├─ Validate link training procedures
Time saved: Parallel design iterations
```

**Box 4: Custom Serial Protocols**
```
Scenario: Proprietary chip design
├─ Characterize custom I/O
├─ System-level pre-silicon verification
├─ Identify tuning parameters early
Time saved: Reduce silicon spins
```

**Visual:**
- Four boxes, each with an icon (PCIe connector, Ethernet, USB, Circuit)
- Each box shows application name and 3-4 bullet points
- Optional: Time savings estimates

**Notes:** Show practical relevance

---

## PAGE 16: LIMITATIONS & TRADE-OFFS

**Title:** Realistic View: What PyAMI Is NOT

**Left Column: NOT a Full Simulator**
```
❌ PyAMI does NOT:
• Simulate analog circuit behavior
• Extract parasitics from layout
• Model thermal effects
• Predict exact silicon timing
• Perform power analysis
• Simulate crosstalk in detail

✓ Use Instead: ADS, HSpice, Cadence
```

**Right Column: Behavioral Model Limitations**
```
⚠️ Important Caveats:
• Models are approximations (by design)
• Validated for typical conditions only
• Process corners may differ significantly
• Environmental factors not included
  - Temperature effects
  - Supply voltage variations
  - Aging/reliability

✓ Always verify: Silicon measurements or SPICE
```

**Bottom: The Trade-Off**
```
Speed ←→ Accuracy

PyAMI:  Fast, approximate, high-level
SPICE:  Slow, detailed, circuit-accurate

Use PyAMI for: Quick exploration, design trade-offs, parameter optimization
Use SPICE for: Final verification, detailed analysis, edge cases
```

**Visual:**
- Two columns with X marks
- Warning icons
- Speed vs. Accuracy slider/spectrum

**Notes:** Set proper expectations

---

## PAGE 17: GETTING STARTED

**Title:** Getting Started with PyAMI: Quick Start Guide

**Section 1: Installation (1 Command)**
```bash
pip install pyibisami
```

**Section 2: Run the Demo (1 Command)**
```bash
python working_demo.py
```

**Output:**
```
✓ 4 configurations tested
✓ 2 plots generated (time + frequency domain)
✓ Console output showing results
```

**Section 3: Customize Parameters (Code Snippet)**
```python
# Change these lines in working_demo.py
bit_rate = 25e9           # Change to 25 Gbps
nspui = 64                # More samples per bit
configs[0]["tx_tap_np1"] = 3  # Different tap value
```

**Section 4: Further Exploration**
```
1. Read WORKING_DEMO_DOCUMENTATION.md
   └─ Detailed explanation of demo results

2. Read COMPREHENSIVE_GUIDE.md
   └─ Full PyAMI capabilities and workflows

3. Modify and experiment
   └─ Try different test signals
   └─ Try different models (example_rx)
   └─ Try different bit rates

4. Create .ibs files
   └─ python -m pyibisami.ami.config tests/examples/example_tx.py
```

**Visual:**
- Command boxes with syntax highlighting
- Numbered steps with arrows
- Links/references to documentation files

**Notes:** Make first steps easy

---

## PAGE 18: SUMMARY & TAKEAWAYS

**Title:** Summary: PyAMI in a Nutshell

**Left Column: WHAT IS PyAMI?**
```
Python toolkit for loading and testing
IBIS-AMI behavioral models of
high-speed I/O (transmitters, receivers)

Fast, easy, industry-standard way to:
• Verify serial link behavior
• Optimize signal integrity
• Make design trade-offs
• Reduce simulation time
```

**Right Column: WHY SHOULD YOU CARE?**
```
✓ Speed: Minutes vs. days for simulation
✓ Accessibility: Simple Python API
✓ Industry Standard: Works everywhere
✓ Practical: Real-world applications
✓ Free & Open Source: Available now

Key insight: Bridge between chip design
and system-level simulation
```

**Bottom: THREE TAKEAWAYS**
```
1️⃣  Pre-emphasis boosts high frequencies to overcome channel loss
    → Transmitter intentionally distorts signal

2️⃣  IBIS-AMI models capture this behavior in a standard format
    → Works with any simulator/tool

3️⃣  PyAMI makes testing these models fast and easy
    → Python makes high-speed testing accessible
```

**Visual:**
- Clean summary boxes
- Three numbered callout boxes at bottom
- Optional: Small icon/graphic for each takeaway

**Notes:** Strong closing message

---

## GENERAL VISUAL NOTES FOR ALL SLIDES

**Color Scheme (Recommended):**
- Primary: Professional Blue (#0052CC or similar)
- Secondary: Light Gray (#F5F5F5)
- Accent: Green (#00AA44) for checkmarks/positive
- Accent: Red (#CC0000) for warnings/negative
- Text: Dark Gray (#333333) on light backgrounds

**Fonts:**
- Title: Sans-serif, 44-54pt, bold
- Body: Sans-serif, 20-28pt, regular
- Code: Monospace, 14-18pt

**Layout:**
- 16:9 widescreen format
- Consistent margins (0.5" all sides)
- Max 5-6 bullet points per slide
- One main visual element per slide

**Visual Assets to Create/Find:**
- Block diagram of PyAMI architecture (Page 7)
- Signal flow diagram (Page 13)
- Icons for applications (Page 15)
- Speed vs. accuracy spectrum (Page 16)

---

## NOTES FOR PRESENTER

- **Total Time:** 15-20 minutes if all slides covered
- **Key Points to Emphasize:**
  - PyAMI simplifies access to behavioral models (Page 2)
  - Pre-emphasis is a practical necessity (Page 11)
  - Demo shows real, working results (Pages 9-10)
  - Limitations are understood (Page 16)
  
- **Possible Audience Questions:**
  - "Why not just use SPICE?" → Answer: Speed/trade-off (Page 16)
  - "How accurate are these models?" → Answer: Industry standard, validated (Page 14)
  - "Can I use this for my design?" → Answer: Yes, getting started is easy (Page 17)

