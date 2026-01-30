# PyAMI & ibisami: Complete Developer Guide

**Date:** January 26, 2026  
**Author:** Comprehensive documentation of the PyAMI and ibisami ecosystem

---

## Table of Contents

1. [Overview](#overview)
2. [PyAMI Repository Deep Dive](#pyami-repository-deep-dive)
3. [ibisami Repository Deep Dive](#ibisami-repository-deep-dive)
4. [How They Work Together](#how-they-work-together)
5. [Complete Workflow](#complete-workflow)
6. [Technical Architecture](#technical-architecture)
7. [Practical Examples](#practical-examples)
8. [Reference](#reference)

---

## Overview

### What is IBIS-AMI?

IBIS stands for "Input/Output Buffer Information Specification," and AMI stands for "Algorithmic Modeling Interface."

- **IBIS files** are detailed descriptions of how electronic components (chips, connectors, etc.) behave electrically. They describe properties like voltage levels, current draw, and impedance.
- **AMI models** are high-speed behavioral models for digital communication systems. They simulate how data signals travel through electronic circuits and get processed by specialized algorithms.

Together, IBIS-AMI is used by electrical engineers to simulate and test high-speed digital signal transmission systems, like those in modern CPUs, memory, and network equipment.

### The Two-Repository Ecosystem

**PyAMI (Python)** - Testing, configuration, and automation toolkit  
**ibisami (C++)** - Signal processing framework and base implementation

These repositories form a complete IBIS-AMI model development ecosystem where:
- **PyAMI** provides Python tools to configure, test, and analyze models
- **ibisami** provides C++ infrastructure to implement high-performance signal processing

---

## PyAMI Repository Deep Dive

### Project Purpose

PyAMI is a Python toolkit for configuring, testing, and analyzing IBIS-AMI models—high-speed behavioral models used in electrical engineering to simulate how digital signals travel through electronic circuits. It automates model generation from Python configurations, runs test suites on compiled models, and produces analysis reports through Jupyter notebooks. It's primarily used by hardware designers and engineers working on high-speed interfaces in CPUs, memory systems, and network equipment.

### Repository Structure

```
PyAMI/
├── src/pyibisami/          # Main Python package
│   ├── __init__.py
│   ├── common.py           # Shared utilities and types
│   ├── ami/                # AMI model handling
│   │   ├── __init__.py
│   │   ├── config.py       # Model configuration tool
│   │   ├── model.py        # AMI model wrapper (loads DLLs)
│   │   ├── parameter.py    # AMI parameter classes
│   │   ├── parser.py       # AMI file parser
│   │   └── reserved_parameter_names.py
│   ├── ibis/               # IBIS file handling
│   │   ├── __init__.py
│   │   ├── file.py         # IBIS file I/O
│   │   ├── model.py        # IBIS component/model classes
│   │   └── parser.py       # IBIS file parser
│   └── tools/              # Command-line tools
│       ├── __init__.py
│       ├── run_notebook.py # Jupyter notebook testing
│       ├── run_tests.py    # EmPy template testing
│       └── test_results.xsl
├── tests/                  # Test suite
│   ├── conftest.py
│   ├── ami/                # AMI module tests
│   ├── ibis/               # IBIS module tests
│   └── examples/           # Working examples
│       ├── example_tx.py
│       └── example_tx.cpp.em
├── examples/               # Legacy examples (Python 2)
├── docs/                   # Sphinx documentation
└── pyproject.toml          # Package configuration
```

### Core Modules

#### 1. AMI Module (`src/pyibisami/ami/`)

**`model.py` - AMI Model Interface**

This is the bridge between Python and compiled C++ AMI models (DLLs/shared objects).

Key classes and functions:
- **`AMIModel`**: Main class that loads and interacts with compiled AMI models
- **`loadWave(filename)`**: Load waveform files (time, voltage pairs)
- **`interpFile(filename, sample_per)`**: Resample waveforms using linear interpolation

The `AMIModel` class uses Python's `ctypes` library to:
1. Load the compiled DLL/SO file
2. Get pointers to `AMI_Init()` and `AMI_GetWave()` functions
3. Call these functions with proper type conversions
4. Return results back to Python

Example usage:
```python
from pyibisami.ami.model import AMIModel

# Load compiled model
model = AMIModel('path/to/model.dll')

# Initialize with impulse response
model.initialize(impulse_response, sample_interval, bit_time, ami_params)

# Process signal
output = model.getWave(input_signal)
```

**`parameter.py` - AMI Parameter System**

Defines the `AMIParameter` class representing individual AMI model parameters:
- **Types**: Float, Integer, String, Boolean, UI (unit interval), Tap
- **Usage**: In, Out, InOut, Info
- **Format**: Value, Range, List

Properties (all read-only after initialization):
- `pname`: Parameter name
- `pusage`: Usage type (In/Out/InOut/Info)
- `ptype`: Data type (Float/Integer/Boolean/String/Tap/UI)
- `pformat`: Format (Value/Range/List)
- `pvalue`: Current value (writable for scripting)
- `pmin`, `pmax`: Range boundaries

Example parameter definition:
```python
{
    'tx_tap_units': {
        'type': 'INT',
        'usage': 'In',
        'format': 'Range',
        'min': 6,
        'max': 27,
        'default': 27,
        'description': '"Total current for FIR filter"'
    }
}
```

**`parser.py` - AMI File Parser**

Parses AMI parameter files using parser combinators (via `parsec` library):
- Reads `.ami` files (S-expression format)
- Validates parameter structure
- Builds parameter tree (reserved + model-specific)
- Provides `AMIParamConfigurator` class for GUI-based parameter editing

The parser handles nested parameters and complex structures:
```
(Reserved_Parameters
    (AMI_Version (Type String) (Value "5.1"))
    (Init_Returns_Impulse (Type Boolean) (Value True))
)
(Model_Specific
    (tx_taps
        (Usage In)
        (Type Integer)
        (Range 0 27 27)
    )
)
```

**`config.py` - Model Configuration Generator**

The `ami-config` command-line tool that generates multiple files from a single Python configuration:

Input: `example_tx.py` containing:
- `ibis_params`: Physical component parameters
- `ami_params`: Algorithm parameters

Output:
- `*.ami`: AMI parameter file
- `*.ibs`: IBIS model file
- Optional C++ code snippets (via EmPy templates)

Uses EmPy templating to generate consistent files across all formats.

#### 2. IBIS Module (`src/pyibisami/ibis/`)

**`model.py` - IBIS Component Classes**

Encapsulates IBIS file components:
- **`Component`**: Represents a chip component (manufacturer, package, pins)
- **`Model`**: Represents electrical models (input/output buffers)

Provides GUI (via Traits/TraitsUI) for browsing IBIS components:
```python
component = Component(subDict)
component()  # Opens GUI
```

**`parser.py` - IBIS File Parser**

Comprehensive parser for IBIS format:
- Handles comments (`|`)
- Parses keywords (`[Component]`, `[Model]`, etc.)
- Extracts tables (voltage-current curves, waveforms)
- Validates syntax

Uses parser combinators for robust parsing of complex IBIS files.

**`file.py` - IBIS File I/O**

Handles reading and writing IBIS files, managing:
- File headers
- Component definitions
- Model specifications
- Package models

#### 3. Common Module (`src/pyibisami/common.py`)

Shared utilities across the package:

**Type Definitions**:
```python
Real = TypeVar("Real", float, float)
Comp = TypeVar("Comp", complex, complex)
Rvec: TypeAlias = npt.NDArray["Real"]  # Real vector
Cvec: TypeAlias = npt.NDArray["Comp"]  # Complex vector
```

**Signal Processing Functions**:
```python
def deconv_same(y: Rvec, x: Rvec) -> Rvec:
    """
    Deconvolve input from output to recover filter response.
    
    Uses least-squares solution with convolution matrix.
    Essential for extracting impulse responses from measurements.
    """
```

**Test Configuration Types**:
```python
TestConfig = tuple[str, tuple[dict[str, Any], dict[str, Any]]]
TestSweep = tuple[str, str, list[TestConfig]]
```

### Command-Line Tools

#### 1. `ami-config`

**Purpose**: Generate AMI, IBIS, and C++ files from Python configuration

**Usage**:
```bash
ami-config example_tx.py
```

**What it does**:
1. Imports the Python configuration file
2. Reads `ibis_params` and `ami_params` dictionaries
3. Processes EmPy templates (if provided)
4. Generates:
   - `*.ami`: AMI parameter tree
   - `*.ibs`: IBIS component and model definitions
   - C++ code snippets for parameter extraction

**Configuration format** (`example_tx.py`):
```python
# IBIS physical parameters (3 values: typ, min, max)
ibis_params = {
    'file_name': 'example_tx.ibs',
    'component': 'Example_Tx',
    'manufacturer': 'YourCompany',
    'r_pkg': [0.1, 0.001, 0.5],      # Ohms
    'l_pkg': [10.e-9, 0.1e-9, 50.e-9], # Henries
    'c_pkg': [1.e-12, 0.01e-12, 5.e-12], # Farads
    'impedance': [50., 45., 55.],    # Ohms
    'voltage_range': [1.8, 1.62, 1.98],  # Volts
}

# AMI algorithm parameters
ami_params = {
    'reserved': {
        'AMI_Version': {
            'type': 'STRING',
            'usage': 'Info',
            'format': 'Value',
            'default': '"5.1"',
        },
    },
    'model': {
        'tx_tap_units': {
            'type': 'INT',
            'usage': 'In',
            'format': 'Range',
            'min': 6,
            'max': 27,
            'default': 27,
        },
    }
}
```

#### 2. `run-notebook`

**Purpose**: Run Jupyter notebooks for comprehensive model testing

**Usage**:
```bash
run-notebook example_tx.ibs 10e9 --nspui 32 --nbits 200
```

**Options**:
- `-n, --notebook PATH`: Custom notebook file
- `-o, --out-dir PATH`: Output directory for results
- `-p, --params TEXT`: Configuration sweep directory
- `--is_tx`: Flag for transmitter model
- `--nspui INTEGER`: Samples per unit interval (default: 32)
- `--nbits INTEGER`: Number of bits to simulate (default: 200)
- `--plot-t-max FLOAT`: Maximum time for plots (default: 5e-10 s)
- `--f-max FLOAT`: Maximum frequency for analysis (default: 40 GHz)
- `--f-step FLOAT`: Frequency step (default: 10 MHz)
- `--fig-x, --fig-y INTEGER`: Plot dimensions in inches

**What it does**:
1. Loads the IBIS-AMI model (DLL)
2. Generates test signals (PRBS patterns, clock signals)
3. Calls `AMI_Init()` with impulse response
4. Optionally calls `AMI_GetWave()` for bit-by-bit processing
5. Generates comprehensive analysis:
   - Impulse responses
   - Frequency responses
   - Eye diagrams
   - Jitter analysis
   - BER (bit error rate) curves
6. Outputs HTML/PDF report

#### 3. `run-tests`

**Purpose**: Run EmPy template-based test suites

**Usage**:
```bash
run-tests --model example_tx.dll --test_dir ./tests/ test1.em test2.em
```

**Options**:
- `-m, --model PATH`: AMI model DLL file
- `-t, --test_dir PATH`: Directory containing test templates
- `-p, --params TEXT`: Model configuration sweeps
- `-x, --xml_file PATH`: XML output file
- `-r, --ref_dir PATH`: Reference waveforms directory
- `-o, --out_dir PATH`: Results output directory

**EmPy Template Example** (`freq_resp.em`):
```python
@# EmPy template for frequency response test
@{
import numpy as np
from pyibisami.ami.model import AMIModel

# Load model
model = AMIModel('@model_file')

# Generate frequency sweep
freqs = np.logspace(6, 12, 100)
response = []

for f in freqs:
    # Test at each frequency
    result = model.test_frequency(f)
    response.append(result)
}@

<test name="Frequency Response">
    <frequencies>@freqs</frequencies>
    <response>@response</response>
</test>
```

**Output**: XML file with test results, viewable in web browser with XSLT stylesheet

### Key Technology Stack

- **NumPy/SciPy**: Signal processing, FFT, filtering, linear algebra
- **ctypes**: Interface with compiled C/C++ DLLs
- **EmPy**: Templating language for test generation
- **Jupyter/Papermill**: Notebook automation and execution
- **Chaco/Traits/TraitsUI**: GUI framework for interactive components
- **parsec**: Parser combinator library for IBIS/AMI parsing
- **Click**: Modern command-line interface framework
- **matplotlib**: Plotting and visualization

### Installation & Dependencies

**From PyPI**:
```bash
pip install PyIBIS-AMI
```

**Requirements** (from `pyproject.toml`):
- Python: >=3.10, <3.13
- chaco>=6.0.0
- click>=8.1.3
- empy>=3.3.4
- importlib_resources
- jupyter
- matplotlib>=3.6.1
- numpy>=1.26,<1.27
- papermill
- parsec>=3.15
- scipy>=1.9

---

## ibisami Repository Deep Dive

### Project Purpose

ibisami is a public domain C++ infrastructure for creating IBIS-AMI models. It provides:
- Base classes for Tx/Rx models
- Reusable signal processing algorithms
- IBIS-AMI API implementation
- Complete working examples

### Repository Structure

```
ibisami/
├── include/                # Header files
│   ├── amimodel.h          # Base model class
│   ├── ami_tx.h            # Transmitter base class
│   ├── ami_rx.h            # Receiver base class
│   ├── fir_filter.h        # FIR filter implementation
│   ├── dfe.h               # Decision feedback equalizer
│   ├── digital_filter.h    # IIR filter implementation
│   ├── cdr.h               # Clock data recovery
│   └── util.h              # Utilities
├── src/                    # Implementation files
│   ├── ibisami_api.cpp     # IBIS-AMI API (AMI_Init, AMI_GetWave, AMI_Close)
│   ├── amimodel.cpp        # Base model implementation
│   ├── ami_tx.cpp          # Tx base implementation
│   ├── ami_rx.cpp          # Rx base implementation
│   ├── fir_filter.cpp      # FIR filter
│   ├── dfe.cpp             # DFE algorithm
│   ├── digital_filter.cpp  # IIR filter (CTLE)
│   └── util.cpp            # Helper functions
├── example/                # Complete working examples
│   ├── example_tx.py       # Tx Python configuration
│   ├── example_tx.cpp      # Tx C++ implementation
│   ├── example_tx.ami      # Generated AMI file
│   ├── example_tx.ibs      # Generated IBIS file
│   ├── example_rx.py       # Rx Python configuration
│   ├── example_rx.cpp      # Rx C++ implementation
│   ├── GNUmakefile         # Build system
│   ├── ibisami_Example_Models_Tester.ipynb  # Test notebook
│   └── tests/              # Test configurations
├── doc/                    # Doxygen documentation
├── GNUmakefile             # Top-level build
├── defs.mak                # Build definitions
└── Creating_IBIS-AMI_Models.pptx  # Tutorial presentation
```

### Core C++ Classes

#### 1. Base Model Infrastructure

**`AMIModel` (amimodel.h/cpp)**

Abstract base class for all AMI models:

```cpp
class AMIModel {
protected:
    double sample_interval_;  // Time between samples
    double bit_time_;         // Unit interval
    std::string msg_;         // Status/error messages
    std::string params_;      // AMI parameter string
    
public:
    // Pure virtual - must be overridden
    virtual void init(
        double *impulse_matrix,
        const long number_of_rows,
        const long aggressors,
        const double sample_interval,
        const double bit_time,
        const std::string& AMI_parameters_in
    ) = 0;
    
    // Called after init to process impulse response
    virtual void proc_imp() = 0;
    
    // Process signal wave (optional, for GetWave mode)
    virtual void proc_sig(double *sig, long len) = 0;
    
    // Accessors
    std::string msg() const { return msg_; }
    std::string params() const { return params_; }
    
    // Parameter extraction helpers
    int get_param_int(const std::vector<std::string>& node_names, int default_val);
    double get_param_float(const std::vector<std::string>& node_names, double default_val);
    bool get_param_bool(const std::vector<std::string>& node_names, bool default_val);
    std::string get_param_str(const std::vector<std::string>& node_names, std::string default_val);
};
```

Key responsibilities:
- Parse AMI parameter tree
- Store model state
- Provide parameter extraction utilities
- Define interface contract

**`AmiTx` (ami_tx.h/cpp)**

Base class for transmitter models:

```cpp
class AmiTx : public AMIModel {
protected:
    std::vector<double> tap_weights_;  // FIR tap coefficients
    bool have_preemph_;                // Pre-emphasis enabled?
    FIRFilter *fir_filter_;            // Optional FIR filter
    
public:
    AmiTx() : have_preemph_(false), fir_filter_(nullptr) {}
    virtual ~AmiTx() { if (fir_filter_) delete fir_filter_; }
    
    void proc_imp() override {
        // Apply pre-emphasis to impulse response
        if (have_preemph_ && !tap_weights_.empty()) {
            fir_filter_ = new FIRFilter(tap_weights_, samples_per_bit_);
            fir_filter_->apply(impulse_matrix_, number_of_rows_);
        }
    }
    
    void proc_sig(double *sig, long len) override {
        // Apply pre-emphasis to signal
        if (fir_filter_) {
            fir_filter_->apply(sig, len);
        }
    }
};
```

Typical Tx functionality:
- FIR pre-emphasis filtering
- De-emphasis
- FFE (feed-forward equalization)

**`AmiRx` (ami_rx.h/cpp)**

Base class for receiver models:

```cpp
class AmiRx : public AMIModel {
protected:
    // CTLE (Continuous Time Linear Equalizer)
    bool have_ctle_;
    DigitalFilter *ctle_filter_;
    double ctle_freq_, ctle_mag_, ctle_bw_, ctle_dcgain_;
    
    // DFE (Decision Feedback Equalizer)
    bool have_dfe_;
    DFE *dfe_;
    int dfe_mode_;
    std::vector<double> dfe_tap_weights_;
    
public:
    AmiRx() : have_ctle_(false), have_dfe_(false), 
              ctle_filter_(nullptr), dfe_(nullptr) {}
    
    void proc_imp() override {
        // Apply CTLE to impulse response
        if (have_ctle_) {
            build_ctle();  // Constructs IIR filter
            ctle_filter_->apply(impulse_matrix_, number_of_rows_);
        }
        // Approximate DFE effect on impulse response
        if (have_dfe_ && dfe_mode_ > 0) {
            approximate_dfe();
        }
    }
    
    void proc_sig(double *sig, long len) override {
        // Apply CTLE
        if (ctle_filter_) {
            ctle_filter_->apply(sig, len);
        }
        // Apply adaptive DFE
        if (dfe_ && dfe_mode_ > 1) {
            dfe_->apply(sig, len, clock_times_);
        }
    }
};
```

Typical Rx functionality:
- CTLE (continuous-time linear equalizer)
- DFE (decision feedback equalizer)
- CDR (clock data recovery)
- AGC (automatic gain control)

#### 2. Signal Processing Algorithms

**`FIRFilter` (fir_filter.h/cpp)**

Finite Impulse Response filter:

```cpp
class FIRFilter {
private:
    std::vector<double> weights_;      // Tap coefficients
    std::vector<double> delay_chain_;  // Signal history
    int oversample_factor_;            // Samples per tap
    
public:
    FIRFilter(const std::vector<double>& weights, int oversample_factor = 1);
    
    void apply(double *sig, const long len) {
        for (auto i = 0; i < len; i++) {
            // Shift new sample into delay chain
            std::rotate(delay_chain_.begin(), 
                       delay_chain_.begin() + 1, 
                       delay_chain_.end());
            delay_chain_.back() = sig[i];
            
            // Compute convolution sum
            double accum = 0.0;
            int j = 0;
            for (auto weight : weights_) {
                accum += weight * delay_chain_[j];
                j += oversample_factor_;
            }
            sig[i] = accum;
        }
    }
    
    double step(double x);  // Single sample processing
    std::vector<double> get_weights();  // Current weights
    std::vector<double> get_values();   // Delay chain contents
};
```

Use cases:
- Pre-emphasis in transmitters
- FFE (feed-forward equalization) in receivers
- Matched filtering

**`DigitalFilter` (digital_filter.h/cpp)**

IIR (Infinite Impulse Response) filter using Direct Form II:

```cpp
class DigitalFilter {
private:
    std::vector<double> num_;    // Numerator coefficients (zeros)
    std::vector<double> den_;    // Denominator coefficients (poles)
    std::vector<double> state_;  // Internal state variables
    int num_taps_;
    
public:
    DigitalFilter(const std::vector<double>& num, 
                  const std::vector<double>& den);
    
    void apply(double *sig, const long len) {
        for (auto i = 0; i < len; i++) {
            // Shift state variables (w values)
            for (auto j = num_taps_ - 1; j > 0; j--)
                state_[j] = state_[j - 1];
            
            // Compute new w[0]
            double accum = sig[i];
            for (auto j = 1; j < num_taps_; j++)
                accum -= state_[j] * den_[j];
            state_[0] = accum;
            
            // Compute output y[n]
            accum = 0;
            for (auto j = 0; j < num_taps_; j++)
                accum += state_[j] * num_[j];
            sig[i] = accum;
        }
    }
};
```

Use cases:
- CTLE (continuous-time linear equalizer approximation)
- Frequency-dependent filtering
- Peaking/boosting specific frequencies

**`DFE` (dfe.h/cpp)**

Decision Feedback Equalizer with adaptation:

```cpp
class DFE {
private:
    double slicer_mag_;              // Output magnitude (0→slicer_mag_)
    double err_gain_;                // LMS adaptation step size
    int mode_;                       // 0=off, 1=init, 2=adaptive
    
    std::vector<double> tap_weights_;     // DFE tap weights
    std::vector<double> min_weights_;     // Min bounds
    std::vector<double> max_weights_;     // Max bounds
    
    FIRFilter *backward_filter_;     // Feedback filter
    double backward_filter_output_;  // Current feedback
    double sample_interval_;
    double clock_per_;               // Clock period (UI)
    double next_clock_;              // Next clock edge time
    
public:
    DFE(double slicer_output_mag, double error_gain, int adapt_mode,
        double sample_interval, double clock_per,
        const std::vector<double>& tap_weights);
    
    bool apply(double *sig, const long len, double *clock_times) {
        for (auto i = 0; i < len; i++) {
            // Subtract feedback from input
            double summer_output = sig[i] - backward_filter_output_;
            
            // Check if at clock instant
            if (sim_time_ >= next_clock_) {
                // Sample signal
                double clk_sample = interp(...);
                
                // Make decision (slicer)
                double decision = slicer_mag_ * sgn(clk_sample);
                
                // Adapt if enabled
                if (mode_ > 1 && cdr_locked_) {
                    double err = clk_sample - decision;
                    std::vector<double> weights = backward_filter_->get_weights();
                    std::vector<double> values = backward_filter_->get_values();
                    
                    // LMS adaptation: w_new = w_old + μ * error * x
                    for (int j = 0; j < weights.size(); j++) {
                        double new_weight = weights[j] + err * err_gain_ * values[j];
                        new_weight = std::clamp(new_weight, min_weights_[j], max_weights_[j]);
                        new_weights.push_back(new_weight);
                    }
                    backward_filter_->set_weights(new_weights);
                }
                
                // Update feedback for next samples
                backward_filter_output_ = backward_filter_->step(decision);
                next_clock_ += clock_per_;
            }
            
            // Output is input minus feedback
            sig[i] = summer_output;
        }
        return true;
    }
};
```

How DFE works:
1. **Feedback loop**: Uses past decisions to predict and cancel ISI
2. **Slicer**: Hard decision on received signal
3. **Adaptation**: LMS algorithm adjusts tap weights to minimize error
4. **Causality**: Only uses past symbols (decision feedback)

#### 3. IBIS-AMI API Implementation

**`ibisami_api.cpp`**

Implements the three required IBIS-AMI functions:

**`AMI_Init()`** - Model initialization:

```cpp
DLL_EXPORT long AMI_Init(
    double * impulse_matrix,      // In/Out: Impulse responses
    long     number_of_rows,      // In: Length of impulses
    long     aggressors,          // In: Number of aggressors
    double   sample_interval,     // In: Time step (seconds)
    double   bit_time,            // In: Unit interval (seconds)
    char   * AMI_parameters_in,   // In: Parameter string
    char  ** AMI_parameters_out,  // Out: Updated parameters
    void  ** AMI_memory_handle,   // Out: Model state pointer
    char  ** msg                  // Out: Status message
) {
    // Allocate persistent state
    AmiPointers *self = new AmiPointers;
    *AMI_memory_handle = self;
    
    // Initialize device-specific model
    try {
        ami_model->init(impulse_matrix, number_of_rows, aggressors,
                       sample_interval, bit_time, AMI_parameters_in);
        ami_model->proc_imp();  // Process impulse response
    } catch(std::runtime_error err) {
        *msg = err.what();
        return 0;  // Failure
    }
    
    // Return updated parameters and message
    self->params = new char[ami_model->params().length() + 1];
    strcpy(self->params, ami_model->params().c_str());
    *AMI_parameters_out = self->params;
    
    self->msg = new char[ami_model->msg().length() + 1];
    strcpy(self->msg, ami_model->msg().c_str());
    *msg = self->msg;
    
    return 1;  // Success
}
```

**`AMI_GetWave()`** - Signal processing:

```cpp
DLL_EXPORT long AMI_GetWave(
    double * wave,              // In/Out: Signal samples
    long     length,            // In: Number of samples
    double * clock_times,       // Out: Clock edge times
    void   * AMI_memory_handle  // In: Model state
) {
    AmiPointers *self = (AmiPointers *)AMI_memory_handle;
    
    if (!self || !self->model) {
        return 0;  // Error
    }
    
    // Process signal through model
    self->model->proc_sig(wave, length);
    
    return 1;  // Success
}
```

**`AMI_Close()`** - Cleanup:

```cpp
DLL_EXPORT long AMI_Close(void * AMI_memory_handle) {
    AmiPointers *self = (AmiPointers *)AMI_memory_handle;
    
    if (self) {
        if (self->msg) delete[] self->msg;
        if (self->params) delete[] self->params;
        delete self;
    }
    
    return 1;  // Success
}
```

Key points:
- **Reentrant**: Uses heap allocation for all state
- **Error handling**: Try-catch with informative messages
- **Memory management**: Caller must call `AMI_Close()`
- **Cross-platform**: Works on Windows (DLL) and Linux (SO)

### Example Models

#### Transmitter Example

**`example/example_tx.py`** - Configuration:

```python
kFileBaseName = 'example_tx'
kDescription = 'Example Tx model from ibisami package.'

# IBIS physical parameters (typ, min, max)
ibis_params = {
    'file_name': 'example_tx.ibs',
    'component': 'Example_Tx',
    'manufacturer': '(n/a)',
    'r_pkg': [0.1, 0.001, 0.5],        # Package resistance (Ω)
    'l_pkg': [10.e-9, 0.1e-9, 50.e-9], # Package inductance (H)
    'c_pkg': [1.e-12, 0.01e-12, 5.e-12], # Package capacitance (F)
    'model_type': 'Output',
    'impedance': [50., 45., 55.],      # Output impedance (Ω)
    'voltage_range': [1.8, 1.62, 1.98], # Supply voltage (V)
    'temperature_range': [25, 0, 100],  # Operating temp (°C)
    'slew_rate': [5.e9, 1.e9, 10.e9],  # Slew rate (V/s)
}

# AMI algorithm parameters
ami_params = {
    'reserved': {
        'AMI_Version': {
            'type': 'STRING',
            'usage': 'Info',
            'default': '"5.1"',
        },
        'Init_Returns_Impulse': {
            'type': 'BOOL',
            'usage': 'Info',
            'default': 'True',
        },
        'GetWave_Exists': {
            'type': 'BOOL',
            'usage': 'Info',
            'default': 'True',
        },
    },
    'model': {
        'tx_tap_units': {
            'type': 'INT',
            'usage': 'In',
            'format': 'Range',
            'min': 6,
            'max': 27,
            'default': 27,
            'description': '"Total current for FIR filter"',
        },
        'tx_tap_np1': {  # Pre-cursor tap
            'type': 'INT',
            'usage': 'In',
            'format': 'Range',
            'min': 0,
            'max': 10,
            'default': 0,
            'tap_pos': 0,
            'description': '"First pre-tap"',
        },
        'tx_tap_nm1': {  # Post-cursor tap 1
            'type': 'INT',
            'usage': 'In',
            'format': 'Range',
            'min': 0,
            'max': 10,
            'default': 0,
            'tap_pos': 2,
            'description': '"First post-tap"',
        },
        'tx_tap_nm2': {  # Post-cursor tap 2
            'type': 'INT',
            'usage': 'In',
            'format': 'Range',
            'min': 0,
            'max': 10,
            'default': 0,
            'tap_pos': 3,
            'description': '"Second post-tap"',
        },
    },
}
```

**`example/example_tx.cpp`** - Implementation:

```cpp
#define TAP_SCALE 0.0407  // Normalization factor

#include "include/ami_tx.h"

class MyTx : public AmiTx {
    typedef AmiTx inherited;
    
public:
    MyTx() {}
    ~MyTx() {}
    
    void init(double *impulse_matrix, const long number_of_rows,
              const long aggressors, const double sample_interval,
              const double bit_time, const std::string& AMI_parameters_in) override {
        
        // Let base class handle common initialization
        inherited::init(impulse_matrix, number_of_rows, aggressors,
                       sample_interval, bit_time, AMI_parameters_in);
        
        // Extract our specific parameters
        std::vector<std::string> node_names;
        std::ostringstream msg;
        
        msg << "Initializing Tx...\n";
        
        // Read tap configuration
        int taps[4];
        node_names.push_back("tx_tap_units");
        int tx_tap_units = get_param_int(node_names, 27);
        node_names.pop_back();
        
        node_names.push_back("tx_tap_np1");
        taps[0] = get_param_int(node_names, 0);  // Pre-cursor
        node_names.pop_back();
        
        node_names.push_back("tx_tap_nm1");
        taps[2] = get_param_int(node_names, 0);  // Post-cursor 1
        node_names.pop_back();
        
        node_names.push_back("tx_tap_nm2");
        taps[3] = get_param_int(node_names, 0);  // Post-cursor 2
        node_names.pop_back();
        
        // Main tap gets remaining current
        taps[1] = tx_tap_units - (taps[0] + taps[2] + taps[3]);
        
        // Validate configuration
        if (tx_tap_units - 2 * (taps[0] + taps[2] + taps[3]) < 6) {
            msg << "WARNING: Illegal Tx pre-emphasis tap configuration!\n";
        }
        
        // Convert to normalized weights
        tap_weights_.clear();
        int samples_per_bit = int(bit_time / sample_interval);
        int tap_signs[] = {-1, 1, -1, -1};  // Pre-emphasis pattern
        
        have_preemph_ = true;
        for (int i = 0; i <= 3; i++) {
            tap_weights_.push_back(taps[i] * TAP_SCALE * tap_signs[i]);
            msg << " (tap_weights_[" << i << "] " << tap_weights_.back() << ")";
            
            // Add zeros between symbol-spaced taps
            for (int j = 1; j < samples_per_bit; j++)
                tap_weights_.push_back(0.0);
        }
        
        msg << "\nTx initialization complete.";
        msg_ = msg.str();
        
        // Build parameter output string
        std::ostringstream params;
        params << "(example_tx";
        params << " (tx_tap_units " << tx_tap_units << ")";
        for (int i = 0; i < 4; i++)
            params << " (taps[" << i << "] " << taps[i] << ")";
        params << ")";
        params_ = params.str();
    }
};

// Global instance (required by ibisami_api.cpp)
AMIModel *ami_model = new MyTx();
```

**How it works**:
1. User specifies tap currents (e.g., pre=2, main=23, post1=1, post2=1)
2. Code converts to normalized weights with TAP_SCALE
3. Applies sign pattern for pre-emphasis: [-pre, +main, -post1, -post2]
4. Base class applies FIR filter to impulse response

Result: High frequencies are boosted to compensate for channel loss

#### Receiver Example

**`example/example_rx.py`** - Key parameters:

```python
ami_params = {
    'model': {
        'ctle_mode': {
            'type': 'INT',
            'usage': 'In',
            'format': 'List',
            'values': [0, 1],
            'labels': ['"Off"', '"Manual"'],
            'default': 0,
        },
        'ctle_freq': {  # Peaking frequency
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': 1.0e9,
            'max': 5.0e9,
            'default': 5.0e9,
            'description': '"CTLE peaking frequency (Hz)"',
        },
        'ctle_mag': {  # Peaking magnitude
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': 0.0,
            'max': 12.0,
            'default': 0.0,
            'description': '"CTLE peaking magnitude (dB)"',
        },
        'dfe_mode': {
            'type': 'INT',
            'usage': 'In',
            'format': 'List',
            'values': [0, 1, 2],
            'labels': ['"Off"', '"Init"', '"Adaptive"'],
            'default': 0,
        },
        'dfe_tap_1': {
            'type': 'FLOAT',
            'usage': 'InOut',
            'format': 'Range',
            'min': -0.5,
            'max': 0.5,
            'default': 0.0,
            'description': '"DFE tap 1 weight"',
        },
        # ... more DFE taps
    }
}
```

**Receiver processing flow**:
1. **CTLE**: IIR filter boosts high frequencies (compensates loss)
2. **DFE**: Adaptive feedback cancels post-cursor ISI
3. **CDR**: Recovers clock from data edges
4. **Slicer**: Makes bit decisions

### Build System

**`GNUmakefile`** (in `example/`):

```makefile
# Build both 32-bit and 64-bit versions
all: x32 x64

x32:
    @echo "Building 32-bit..."
    MACHINE=X86 $(MAKE) example_tx.dll example_rx.dll

x64:
    @echo "Building 64-bit..."
    MACHINE=AMD64 $(MAKE) example_tx.dll example_rx.dll

# Link model with ibisami library
example_tx.dll: example_tx.o $(IBISAMI_OBJS)
    $(CXX) -shared -o $@ $^ $(LDFLAGS)

example_tx.o: example_tx.cpp
    $(CXX) $(CXXFLAGS) -c -o $@ $<
```

**Dependencies**:
- C++11 or later compiler (g++, clang++, MSVC)
- Make or GNU Make
- Standard library only (no external dependencies)

**Cross-platform support**:
- Linux: Builds `.so` files
- Windows: Builds `.dll` files (with MSVC or MinGW)
- macOS: Builds `.dylib` files

---

## How They Work Together

### The Complete Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                     IBIS-AMI MODEL DEVELOPMENT                   │
│                        COMPLETE ECOSYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 1: DESIGN (ibisami C++ framework)                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

ibisami/
├── include/          ← Inherit from these base classes
│   ├── amimodel.h       • Abstract base for all models
│   ├── ami_tx.h         • Tx base (FIR, pre-emphasis)
│   ├── ami_rx.h         • Rx base (CTLE, DFE, CDR)
│   ├── fir_filter.h     • Reusable FIR filter
│   ├── dfe.h            • Adaptive DFE algorithm
│   └── digital_filter.h • IIR filter (CTLE)
│
├── src/              ← Link against these implementations
│   ├── ibisami_api.cpp  • Standard IBIS-AMI API
│   ├── ami_tx.cpp       • Tx common functionality
│   ├── ami_rx.cpp       • Rx common functionality
│   └── [algorithms].cpp • Signal processing
│
└── example/          ← Your custom implementation
    ├── my_model.cpp     • Your device-specific code
    └── my_model.py      • Your parameter definitions

Your code:
────────────────────────────────────────────────────────
#include "include/ami_tx.h"

class MyTx : public AmiTx {
    void init(...) override {
        // Read parameters
        int tap_value = get_param_int(node_names, default);
        
        // Configure algorithm
        tap_weights_.push_back(tap_value * SCALE);
        
        // Base class handles FIR filtering
        have_preemph_ = true;
    }
};

AMIModel *ami_model = new MyTx();  // Required global
────────────────────────────────────────────────────────

                              ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 2: CONFIGURE (PyAMI tools)                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

my_model.py (Python configuration):
────────────────────────────────────────────────────────
ibis_params = {
    'file_name': 'my_model.ibs',
    'r_pkg': [0.1, 0.001, 0.5],  # Typ, min, max
    'impedance': [50., 45., 55.],
    # ... physical parameters
}

ami_params = {
    'reserved': {
        'AMI_Version': {...},
    },
    'model': {
        'my_tap': {
            'type': 'INT',
            'usage': 'In',
            'min': 0,
            'max': 10,
            'default': 5,
        },
        # ... algorithm parameters
    }
}
────────────────────────────────────────────────────────

$ ami-config my_model.py    ← PyAMI tool
                              ↓
Generates:
  ✓ my_model.ami  (AMI parameter tree)
  ✓ my_model.ibs  (IBIS component/model)
  ✓ [Optional C++ snippets via EmPy]

                              ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 3: COMPILE (ibisami build system)                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

$ make    ← In ibisami/example/

Links together:
  • my_model.cpp (your implementation)
  • ami_tx.cpp (base class)
  • ibisami_api.cpp (IBIS-AMI interface)
  • fir_filter.cpp, dfe.cpp, etc. (algorithms)
                              ↓
Output: my_model.dll (or .so on Linux)

This DLL exports:
  • AMI_Init()    - Initialize and process impulse
  • AMI_GetWave() - Process signal samples
  • AMI_Close()   - Cleanup

                              ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 4: TEST & ANALYZE (PyAMI tools)                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Option A: Jupyter Notebook Testing
────────────────────────────────────────────────────────
$ run-notebook my_model.ibs 10e9    ← PyAMI tool

PyAMI loads my_model.dll via ctypes:
────────────────────────────────────────────────────────
from pyibisami.ami.model import AMIModel

model = AMIModel('my_model.dll')
model.initialize(impulse, sample_int, bit_time, params)
output = model.getWave(input_signal)

plot_frequency_response(output)
plot_eye_diagram(output)
calculate_ber(output)
────────────────────────────────────────────────────────

Output:
  • HTML/PDF report
  • Frequency response plots
  • Eye diagrams
  • Jitter analysis
  • BER curves

Option B: EmPy Template Testing
────────────────────────────────────────────────────────
$ run-tests --model my_model.dll test1.em test2.em

EmPy templates define test scenarios:
────────────────────────────────────────────────────────
@{
from pyibisami.ami.model import AMIModel
model = AMIModel('@model_dll')
# ... test logic in Python/EmPy
}@
<test name="My Test">
  <results>@results</results>
</test>
────────────────────────────────────────────────────────

Output:
  • XML results
  • Viewable in browser (with XSLT)
  • Pass/fail status
  • Performance metrics
```

### Integration Points in Detail

#### 1. Parameter Flow: Python → AMI → C++

**Step 1: Python Definition**
```python
# my_model.py
ami_params = {
    'model': {
        'my_tap': {
            'type': 'INT',
            'usage': 'In',
            'format': 'Range',
            'min': 0,
            'max': 10,
            'default': 5,
            'description': '"My custom tap weight"',
        }
    }
}
```

**Step 2: PyAMI Generates AMI File**
```bash
$ ami-config my_model.py
```

Creates `my_model.ami`:
```
(Model_Specific
    (my_tap
        (Usage In)
        (Type Integer)
        (Range 0 10 5)
        (Description "My custom tap weight")
    )
)
```

**Step 3: Simulator Reads AMI**
When a simulator (or PyAMI test) loads the model:
1. Reads `my_model.ami` to get parameter structure
2. Presents GUI for user to modify values
3. User sets `my_tap = 7`
4. Simulator builds parameter string:
   ```
   (my_model (my_tap 7))
   ```

**Step 4: C++ Model Receives Parameters**
```cpp
void MyModel::init(..., const std::string& AMI_parameters_in) {
    // AMI_parameters_in = "(my_model (my_tap 7))"
    
    inherited::init(..., AMI_parameters_in);  // Base class parses
    
    // Extract value
    std::vector<std::string> node_names;
    node_names.push_back("my_tap");
    int tap_value = get_param_int(node_names, 5);  // Returns 7
    
    // Use it
    configure_algorithm(tap_value);
}
```

The `get_param_int()` method (from `AMIModel` base class):
- Traverses parameter tree using node_names
- Returns user-specified value (7) if found
- Returns default (5) if not found
- Handles type conversion and error checking

#### 2. Signal Processing Flow

**Initialization (AMI_Init)**:
```
Simulator                 ibisami_api.cpp          Your Model
────────                  ───────────────          ──────────
    │                            │                       │
    │ AMI_Init(impulse, ...)     │                       │
    ├───────────────────────────>│                       │
    │                            │ ami_model->init()     │
    │                            ├──────────────────────>│
    │                            │                       │ Read params
    │                            │                       │ Configure
    │                            │                       │ Setup filters
    │                            │                       │
    │                            │  Return               │
    │                            │<──────────────────────┤
    │                            │ ami_model->proc_imp() │
    │                            ├──────────────────────>│
    │                            │                       │ Apply filter
    │                            │                       │ to impulse
    │                            │                       │
    │ Return processed impulse   │  Return               │
    │<───────────────────────────┤<──────────────────────┤
    │                            │                       │
```

**Signal Processing (AMI_GetWave)**:
```
Simulator                 ibisami_api.cpp          Your Model
────────                  ───────────────          ──────────
    │                            │                       │
    │ AMI_GetWave(wave, ...)     │                       │
    ├───────────────────────────>│                       │
    │                            │ ami_model->proc_sig() │
    │                            ├──────────────────────>│
    │                            │                       │ Apply CTLE
    │                            │                       │ Apply DFE
    │                            │                       │ Adapt taps
    │                            │                       │
    │ Return processed wave      │  Return               │
    │<───────────────────────────┤<──────────────────────┤
    │                            │                       │
```

#### 3. PyAMI Testing Interface

**AMIModel Wrapper** (`pyibisami/ami/model.py`):

```python
from ctypes import CDLL, c_double, c_long, c_char_p, byref, pointer

class AMIModel:
    def __init__(self, dll_file: str):
        """Load compiled AMI model DLL."""
        self._ami_model = CDLL(dll_file)
        
        # Get function pointers
        self._ami_init = self._ami_model.AMI_Init
        self._ami_init.restype = c_long
        self._ami_init.argtypes = [
            np.ctypeslib.ndpointer(dtype=c_double),  # impulse_matrix
            c_long,                                   # number_of_rows
            c_long,                                   # aggressors
            c_double,                                 # sample_interval
            c_double,                                 # bit_time
            c_char_p,                                 # AMI_parameters_in
            POINTER(c_char_p),                        # AMI_parameters_out
            POINTER(c_void_p),                        # AMI_memory_handle
            POINTER(c_char_p),                        # msg
        ]
        
        self._ami_getwave = self._ami_model.AMI_GetWave
        # ... similar setup
    
    def initialize(self, impulse: np.ndarray, sample_interval: float,
                   bit_time: float, params: str):
        """Call AMI_Init()."""
        params_out = c_char_p()
        handle = c_void_p()
        msg = c_char_p()
        
        result = self._ami_init(
            impulse,
            len(impulse),
            0,  # No aggressors
            sample_interval,
            bit_time,
            params.encode(),
            byref(params_out),
            byref(handle),
            byref(msg)
        )
        
        if result == 0:
            raise RuntimeError(f"AMI_Init failed: {msg.value.decode()}")
        
        self._handle = handle
        return params_out.value.decode()
    
    def getWave(self, wave: np.ndarray):
        """Call AMI_GetWave()."""
        clock_times = np.zeros(len(wave))
        
        result = self._ami_getwave(
            wave,
            len(wave),
            clock_times,
            self._handle
        )
        
        if result == 0:
            raise RuntimeError("AMI_GetWave failed")
        
        return wave, clock_times
```

**Jupyter Notebook Testing** (generated by `run-notebook`):

```python
import numpy as np
import matplotlib.pyplot as plt
from pyibisami.ami.model import AMIModel

# Configuration
bit_rate = 10e9  # 10 Gbps
nspui = 32       # Samples per UI
nbits = 200      # Number of bits

# Calculate timing
ui = 1.0 / bit_rate
sample_interval = ui / nspui

# Generate impulse response (from channel simulation)
impulse = load_channel_impulse_response()

# Load model
tx_model = AMIModel('example_tx.dll')
rx_model = AMIModel('example_rx.dll')

# Initialize
tx_params = "(example_tx (tx_tap_units 27) (tx_tap_np1 2))"
tx_params_out = tx_model.initialize(impulse, sample_interval, ui, tx_params)

# Generate test signal
bits = np.random.randint(0, 2, nbits)
signal = generate_prbs(bits, nspui)

# Process through Tx
tx_output, _ = tx_model.getWave(signal.copy())

# Simulate channel
channel_output = convolve_with_channel(tx_output, impulse)

# Process through Rx
rx_params = "(example_rx (ctle_mode 1) (dfe_mode 2))"
rx_params_out = rx_model.initialize(impulse, sample_interval, ui, rx_params)
rx_output, clock_times = rx_model.getWave(channel_output.copy())

# Analysis
plot_eye_diagram(rx_output, ui, nspui)
plot_frequency_response(tx_output, sample_interval)
ber = calculate_ber(rx_output, bits, clock_times, ui)

print(f"BER: {ber}")
```

---

## Complete Workflow

### Scenario: Building a Custom Transmitter Model

**Goal**: Create a 4-tap FIR pre-emphasis filter for a 10 Gbps transmitter

#### Step 1: Design Your Model (ibisami)

**1a. Write Python Configuration** (`ibisami/example/my_tx.py`):

```python
kFileBaseName = 'my_tx'
kDescription = 'Custom 4-tap pre-emphasis transmitter'

ibis_params = {
    'file_name': 'my_tx.ibs',
    'file_rev': 'v1.0',
    'copyright': 'Copyright (c) 2026 MyCompany',
    'component': 'MyTx_10G',
    'manufacturer': 'MyCompany Inc.',
    
    # Package parasitics (typ, min, max)
    'r_pkg': [0.2, 0.1, 0.3],          # Resistance (Ω)
    'l_pkg': [15.e-9, 10.e-9, 20.e-9], # Inductance (H)
    'c_pkg': [2.e-12, 1.e-12, 3.e-12], # Capacitance (F)
    
    # Model characteristics
    'model_name': 'my_tx',
    'model_type': 'Output',
    'c_comp': [2.e-12, 1.e-12, 3.e-12],
    'impedance': [50., 48., 52.],
    'voltage_range': [1.2, 1.14, 1.26],  # Core voltage
    'temperature_range': [85, -40, 125],  # Industrial
    'slew_rate': [8.e9, 6.e9, 10.e9],
}

ami_params = {
    'reserved': {
        'AMI_Version': {
            'type': 'STRING',
            'usage': 'Info',
            'format': 'Value',
            'default': '"7.0"',
            'description': '"IBIS-AMI version"',
        },
        'Init_Returns_Impulse': {
            'type': 'BOOL',
            'usage': 'Info',
            'format': 'Value',
            'default': 'True',
            'description': '"Model processes impulse in Init()"',
        },
        'GetWave_Exists': {
            'type': 'BOOL',
            'usage': 'Info',
            'format': 'Value',
            'default': 'True',
            'description': '"Model supports GetWave()"',
        },
    },
    'model': {
        'preset': {
            'type': 'INT',
            'usage': 'In',
            'format': 'List',
            'values': [0, 1, 2, 3],
            'labels': ['"Off"', '"Light"', '"Medium"', '"Strong"'],
            'default': 0,
            'description': '"Pre-emphasis preset"',
        },
        'custom_enable': {
            'type': 'BOOL',
            'usage': 'In',
            'format': 'Value',
            'default': 'False',
            'description': '"Enable custom tap configuration"',
        },
        'pre_tap': {
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': -0.3,
            'max': 0.0,
            'default': 0.0,
            'description': '"Pre-cursor tap weight"',
        },
        'post_tap1': {
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': -0.3,
            'max': 0.0,
            'default': 0.0,
            'description': '"Post-cursor tap 1 weight"',
        },
        'post_tap2': {
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': -0.3,
            'max': 0.0,
            'default': 0.0,
            'description': '"Post-cursor tap 2 weight"',
        },
    }
}
```

**1b. Write C++ Implementation** (`ibisami/example/my_tx.cpp`):

```cpp
#include <sstream>
#include <vector>
#include "include/ami_tx.h"

class MyTx : public AmiTx {
    typedef AmiTx inherited;
    
private:
    // Preset configurations: [pre, main, post1, post2]
    static constexpr double PRESETS[4][4] = {
        {0.0, 1.0, 0.0, 0.0},      // Off
        {-0.05, 1.0, -0.05, 0.0},  // Light
        {-0.10, 1.0, -0.10, -0.05}, // Medium
        {-0.15, 1.0, -0.15, -0.10}, // Strong
    };
    
public:
    MyTx() {}
    ~MyTx() {}
    
    void init(double *impulse_matrix, const long number_of_rows,
              const long aggressors, const double sample_interval,
              const double bit_time, const std::string& AMI_parameters_in) override {
        
        // Base class initialization
        inherited::init(impulse_matrix, number_of_rows, aggressors,
                       sample_interval, bit_time, AMI_parameters_in);
        
        std::vector<std::string> node_names;
        std::ostringstream msg;
        msg << "Initializing MyTx model...\n";
        
        // Read parameters
        node_names.push_back("preset");
        int preset = get_param_int(node_names, 0);
        node_names.pop_back();
        
        node_names.push_back("custom_enable");
        bool custom = get_param_bool(node_names, false);
        node_names.pop_back();
        
        double taps[4];
        
        if (custom) {
            msg << "Using custom tap configuration:\n";
            
            node_names.push_back("pre_tap");
            taps[0] = get_param_float(node_names, 0.0);
            node_names.pop_back();
            
            // Main tap is always 1.0
            taps[1] = 1.0;
            
            node_names.push_back("post_tap1");
            taps[2] = get_param_float(node_names, 0.0);
            node_names.pop_back();
            
            node_names.push_back("post_tap2");
            taps[3] = get_param_float(node_names, 0.0);
            node_names.pop_back();
        } else {
            msg << "Using preset " << preset << ":\n";
            for (int i = 0; i < 4; i++) {
                taps[i] = PRESETS[preset][i];
            }
        }
        
        // Build tap weight vector
        tap_weights_.clear();
        int samples_per_bit = int(bit_time / sample_interval);
        
        for (int tap = 0; tap < 4; tap++) {
            tap_weights_.push_back(taps[tap]);
            msg << "  tap[" << tap << "] = " << taps[tap] << "\n";
            
            // Symbol-spaced: add zeros between taps
            for (int j = 1; j < samples_per_bit; j++) {
                tap_weights_.push_back(0.0);
            }
        }
        
        // Enable pre-emphasis processing
        have_preemph_ = (preset > 0 || custom);
        
        msg << "MyTx initialization complete.\n";
        msg_ = msg.str();
        
        // Build output parameter string
        std::ostringstream params;
        params << "(my_tx";
        params << " (preset " << preset << ")";
        params << " (custom_enable " << (custom ? "True" : "False") << ")";
        for (int i = 0; i < 4; i++) {
            params << " (tap" << i << " " << taps[i] << ")";
        }
        params << ")";
        params_ = params.str();
    }
};

// Required global instance
AMIModel *ami_model = new MyTx();
```

**1c. Update Makefile** (`ibisami/example/GNUmakefile`):

Add target:
```makefile
my_tx.dll: my_tx.o $(IBISAMI_OBJS)
    $(CXX) -shared -o $@ $^ $(LDFLAGS)

my_tx.o: my_tx.cpp
    $(CXX) $(CXXFLAGS) -I.. -c $<
```

#### Step 2: Generate Configuration Files (PyAMI)

```bash
$ cd ibisami/example
$ ami-config my_tx.py
```

**Output**:
- `my_tx.ami`: Full AMI parameter tree with all parameters
- `my_tx.ibs`: IBIS component definition with package model

Verification:
```bash
$ cat my_tx.ami
(Model my_tx
  (Description "Custom 4-tap pre-emphasis transmitter")
  (Reserved_Parameters
    (AMI_Version (Type String) (Value "7.0"))
    (Init_Returns_Impulse (Type Boolean) (Value True))
    (GetWave_Exists (Type Boolean) (Value True))
  )
  (Model_Specific
    (preset
      (Usage In)
      (Type Integer)
      (List 0 1 2 3)
      (List_Tip "Off" "Light" "Medium" "Strong")
      (Description "Pre-emphasis preset")
    )
    (custom_enable
      (Usage In)
      (Type Boolean)
      (Value False)
      (Description "Enable custom tap configuration")
    )
    ...
  )
)
```

#### Step 3: Compile (ibisami)

```bash
$ cd ibisami/example
$ make my_tx.dll
```

**Build process**:
1. Compile `my_tx.cpp` → `my_tx.o`
2. Compile ibisami library sources → `*.o` files
3. Link all together → `my_tx.dll` (Windows) or `my_tx.so` (Linux)

**Verification**:
```bash
$ ls -lh my_tx.dll
-rwxr-xr-x 1 user user 245K Jan 26 10:15 my_tx.dll

$ file my_tx.dll
my_tx.dll: PE32+ executable (DLL) x86-64, for MS Windows
```

The DLL exports three functions:
- `AMI_Init`
- `AMI_GetWave`
- `AMI_Close`

#### Step 4: Test (PyAMI)

**4a. Quick Test with Python Script**:

```python
#!/usr/bin/env python3
# test_my_tx.py

import numpy as np
import matplotlib.pyplot as plt
from pyibisami.ami.model import AMIModel

# Parameters
bit_rate = 10e9
ui = 1.0 / bit_rate
nspui = 32
sample_interval = ui / nspui

# Generate ideal impulse
impulse_len = 100 * nspui
impulse = np.zeros(impulse_len)
impulse[0] = 1.0

# Load model
model = AMIModel('./my_tx.dll')

# Test preset 2 (medium)
params = "(my_tx (preset 2) (custom_enable False))"
params_out = model.initialize(impulse.copy(), sample_interval, ui, params)

print("Model returned:", params_out)

# Get impulse response
impulse_out = impulse.copy()
model._ami_getwave(impulse_out, len(impulse_out), 
                   np.zeros(len(impulse_out)), model._handle)

# Plot
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(impulse[:200])
plt.title('Input Impulse')
plt.xlabel('Sample')

plt.subplot(1, 2, 2)
plt.plot(impulse_out[:200])
plt.title('Pre-emphasized Impulse')
plt.xlabel('Sample')

plt.tight_layout()
plt.savefig('my_tx_impulse.png')
print("Saved: my_tx_impulse.png")

# Frequency response
fft_len = 1024
freq = np.fft.rfftfreq(fft_len, sample_interval)
H = np.fft.rfft(impulse_out, fft_len)
H_dB = 20 * np.log10(np.abs(H) + 1e-10)

plt.figure(figsize=(10, 4))
plt.plot(freq / 1e9, H_dB)
plt.xlabel('Frequency (GHz)')
plt.ylabel('Magnitude (dB)')
plt.title('Tx Frequency Response')
plt.grid(True)
plt.savefig('my_tx_frequency.png')
print("Saved: my_tx_frequency.png")
```

Run:
```bash
$ python test_my_tx.py
Model returned: (my_tx (preset 2) (custom_enable False) (tap0 -0.1) (tap1 1.0) (tap2 -0.1) (tap3 -0.05))
Saved: my_tx_impulse.png
Saved: my_tx_frequency.png
```

**4b. Full Analysis with Jupyter Notebook**:

```bash
$ run-notebook my_tx.ibs 10e9 --is_tx --nspui 32 --nbits 1000
```

This generates a complete Jupyter notebook that:
1. Loads `my_tx.dll`
2. Tests all presets (0, 1, 2, 3)
3. Tests custom tap configurations
4. Generates plots:
   - Impulse responses
   - Frequency responses (showing high-frequency boost)
   - Eye diagrams (if combined with channel)
   - S-parameters
5. Outputs HTML report: `my_tx_analysis.html`

**4c. EmPy Template Testing**:

Create test template (`tests/sweep_presets.em`):
```python
@# Test all presets
@{
from pyibisami.ami.model import AMIModel
import numpy as np

model = AMIModel('@model_file')
bit_rate = @bit_rate
ui = 1.0 / bit_rate
nspui = @nspui
sample_interval = ui / nspui

impulse = np.zeros(100 * nspui)
impulse[0] = 1.0

results = []
for preset in range(4):
    params = f"(my_tx (preset {preset}))"
    model.initialize(impulse.copy(), sample_interval, ui, params)
    # ... process and measure
    results.append(measurement)
}@

<test name="Preset Sweep">
  @[for preset, result in enumerate(results)]
    <preset id="@preset">
      <result>@result</result>
    </preset>
  @[end for]
</test>
```

Run:
```bash
$ run-tests --model my_tx.dll --xml_file results.xml sweep_presets.em
```

View `results.xml` in browser to see formatted test results.

#### Step 5: Validation & Iteration

**Analyze results**:
- Check frequency response has desired peaking
- Verify impulse response shape
- Ensure stability (no ringing)
- Validate against measurements (if available)

**Iterate if needed**:
1. Modify `my_tx.py` (change parameter ranges)
2. Regenerate: `ami-config my_tx.py`
3. Recompile: `make my_tx.dll`
4. Retest: `python test_my_tx.py`

**No need to modify C++ unless**:
- Algorithm changes (new filters, different structure)
- New parameters (add to both .py and .cpp)

#### Step 6: Deployment

**Package for distribution**:
```
my_tx_model_v1.0/
├── my_tx.dll (or .so)
├── my_tx.ami
├── my_tx.ibs
├── README.txt
└── test_results/
    └── my_tx_analysis.html
```

**Users can**:
- Load in commercial simulators (Cadence, Synopsys, Keysight)
- Adjust parameters through simulator GUI
- Run channel simulations
- Validate against their designs

---

## Technical Architecture

### Design Patterns

#### 1. Template Method Pattern (C++ Base Classes)

```cpp
// Abstract base class defines algorithm skeleton
class AMIModel {
public:
    // Template method
    void run() {
        init(...);      // Step 1: Subclass implements
        proc_imp();     // Step 2: Subclass implements
        proc_sig(...);  // Step 3: Subclass implements
    }
    
    // Abstract methods (pure virtual)
    virtual void init(...) = 0;
    virtual void proc_imp() = 0;
    virtual void proc_sig(...) = 0;
};

// Concrete implementation
class MyTx : public AMIModel {
public:
    void init(...) override {
        // Custom initialization
    }
    void proc_imp() override {
        // Apply pre-emphasis to impulse
    }
    void proc_sig(...) override {
        // Apply pre-emphasis to signal
    }
};
```

Benefits:
- Code reuse (parameter parsing, API handling)
- Consistent interface
- Easy to extend

#### 2. Strategy Pattern (Signal Processing Algorithms)

```cpp
// Context
class AmiRx {
private:
    DigitalFilter *ctle_filter_;  // Strategy 1
    DFE *dfe_;                    // Strategy 2
    
public:
    void proc_sig(double *sig, long len) {
        // Use strategies
        if (ctle_filter_)
            ctle_filter_->apply(sig, len);
        
        if (dfe_)
            dfe_->apply(sig, len, clock_times);
    }
};

// Strategies (interchangeable algorithms)
class DigitalFilter {
    virtual void apply(double *sig, long len);
};

class DFE {
    virtual void apply(double *sig, long len, double *clk);
};
```

Benefits:
- Algorithms are interchangeable
- Easy to add new filters
- Can enable/disable at runtime

#### 3. Factory Pattern (Parameter Creation)

```python
# PyAMI parameter factory
class AMIParameter:
    @staticmethod
    def from_dict(name, param_dict):
        """Create parameter from dictionary."""
        type_map = {
            'INT': IntParameter,
            'FLOAT': FloatParameter,
            'BOOL': BoolParameter,
            'STRING': StringParameter,
        }
        param_class = type_map[param_dict['type']]
        return param_class(name, param_dict)
```

#### 4. Adapter Pattern (ctypes Interface)

```python
# PyAMI adapts C API to Python
class AMIModel:
    """Adapter: Python interface to C API."""
    
    def initialize(self, impulse, sample_int, bit_time, params):
        # Adapt Python types to C types
        impulse_c = impulse.ctypes.data_as(POINTER(c_double))
        params_c = c_char_p(params.encode())
        
        # Call C function
        result = self._ami_init(impulse_c, len(impulse), ...)
        
        # Adapt C return to Python
        return result
```

### Memory Management

#### C++ Side (ibisami)

**Heap allocation for reentrancy**:
```cpp
DLL_EXPORT long AMI_Init(..., void **AMI_memory_handle, ...) {
    // Allocate model state on heap
    AmiPointers *self = new AmiPointers;
    self->model = ami_model;
    *AMI_memory_handle = self;  // Pass handle back to caller
    
    return 1;
}

DLL_EXPORT long AMI_Close(void *AMI_memory_handle) {
    // Clean up heap allocation
    AmiPointers *self = (AmiPointers *)AMI_memory_handle;
    delete self;
    return 1;
}
```

**Why heap allocation?**
- Multiple instances can coexist (multi-threading)
- State persists between `AMI_Init()` and `AMI_Close()`
- No global variables (except device-specific model template)

#### Python Side (PyAMI)

**ctypes memory management**:
```python
class AMIModel:
    def __init__(self, dll_file):
        self._dll = CDLL(dll_file)  # Keeps DLL loaded
        self._handle = None         # Stores AMI_memory_handle
    
    def __del__(self):
        """Cleanup when Python object deleted."""
        if self._handle:
            self._ami_close(self._handle)
        # ctypes automatically unloads DLL
```

**NumPy array handling**:
```python
# Zero-copy: Pass NumPy array directly to C
impulse = np.zeros(1000, dtype=np.float64)
self._ami_init(
    impulse.ctypes.data_as(POINTER(c_double)),
    len(impulse),
    ...
)
# impulse array is modified in-place by C code
```

### Performance Considerations

#### 1. Vectorization (NumPy/C++)

**Good practice** (vectorized):
```cpp
// Process entire array at once
void FIRFilter::apply(double *sig, const long len) {
    for (long i = 0; i < len; i++) {
        // Loop is compiled with SIMD by compiler
        sig[i] = compute_sample(sig[i]);
    }
}
```

**Avoid** (scalar processing):
```python
# Calling C function for each sample (slow!)
for sample in signal:
    model.process_one_sample(sample)
```

#### 2. Algorithm Complexity

**FIR Filter**: O(N × M) where N = samples, M = taps
- 4 taps, 10,000 samples = 40,000 operations
- Highly parallelizable (no feedback)

**IIR Filter**: O(N × M) but with dependencies
- Cannot be fully parallelized (feedback loop)
- State updates must be sequential

**DFE**: O(N × M) with additional decision logic
- Most complex (adaptation, clock recovery)
- Typically M < 10 taps (post-cursor ISI)

#### 3. Memory Access Patterns

**Cache-friendly** (sequential):
```cpp
// Good: Sequential access
for (int i = 0; i < len; i++) {
    sig[i] = filter(sig[i]);  // Stride-1 access
}
```

**Cache-unfriendly** (random):
```cpp
// Bad: Random access
for (int i = 0; i < len; i++) {
    sig[random_indices[i]] = ...;  // Cache misses
}
```

### Error Handling

#### C++ Side

**Exception handling**:
```cpp
long AMI_Init(...) {
    try {
        ami_model->init(...);
        ami_model->proc_imp();
    } catch (std::runtime_error& err) {
        // Convert exception to error message
        *msg = err.what();
        return 0;  // Indicate failure
    } catch (...) {
        *msg = "Unknown error";
        return 0;
    }
    return 1;  // Success
}
```

**Defensive programming**:
```cpp
void MyTx::init(...) {
    // Validate inputs
    if (sample_interval <= 0) {
        throw std::runtime_error("Invalid sample interval");
    }
    
    // Check parameter ranges
    int tap_value = get_param_int(node_names, default_val);
    if (tap_value < min_tap || tap_value > max_tap) {
        std::ostringstream err;
        err << "Tap value " << tap_value << " out of range";
        throw std::runtime_error(err.str());
    }
}
```

#### Python Side

**Graceful failure**:
```python
class AMIModel:
    def initialize(self, ...):
        result = self._ami_init(...)
        if result == 0:
            # Model indicated failure
            error_msg = self._msg.value.decode()
            raise RuntimeError(f"AMI_Init failed: {error_msg}")
        
        # Success: return updated parameters
        return self._params_out.value.decode()
```

**Validation**:
```python
def validate_parameters(params):
    """Validate parameter string before passing to C."""
    if not params.startswith('('):
        raise ValueError("Parameters must be S-expression")
    
    # Could parse and validate structure
    # ...
```

---

## Practical Examples

### Example 1: Parameter Sweep

**Goal**: Test transmitter with different pre-emphasis settings

```python
#!/usr/bin/env python3
# sweep_tx_presets.py

import numpy as np
import matplotlib.pyplot as plt
from pyibisami.ami.model import AMIModel

# Setup
model = AMIModel('./example_tx.dll')
bit_rate = 10e9
ui = 1.0 / bit_rate
nspui = 32
sample_interval = ui / nspui

# Generate impulse
impulse_len = 200 * nspui
impulse = np.zeros(impulse_len)
impulse[50 * nspui] = 1.0  # Delay for causality

# Test each preset
presets = ['Off', 'Light', 'Medium', 'Strong']
results = {}

plt.figure(figsize=(14, 10))

for i, preset_name in enumerate(presets):
    # Configure
    params = f"(example_tx (preset {i}))"
    
    # Initialize
    impulse_test = impulse.copy()
    params_out = model.initialize(impulse_test, sample_interval, ui, params)
    
    # Process
    impulse_out = impulse_test.copy()
    model._ami_getwave(impulse_out, len(impulse_out),
                       np.zeros(len(impulse_out)), model._handle)
    
    results[preset_name] = impulse_out
    
    # Plot impulse response
    plt.subplot(2, 2, i + 1)
    time_ns = np.arange(len(impulse_out)) * sample_interval * 1e9
    plt.plot(time_ns[:400], impulse_out[:400])
    plt.title(f'Preset: {preset_name}')
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude')
    plt.grid(True)

plt.tight_layout()
plt.savefig('tx_preset_sweep.png', dpi=150)
print("Saved: tx_preset_sweep.png")

# Frequency domain comparison
plt.figure(figsize=(10, 6))
fft_len = 4096
freq_ghz = np.fft.rfftfreq(fft_len, sample_interval) / 1e9

for preset_name, impulse_out in results.items():
    H = np.fft.rfft(impulse_out, fft_len)
    H_dB = 20 * np.log10(np.abs(H) + 1e-12)
    plt.plot(freq_ghz, H_dB, label=preset_name, linewidth=2)

plt.xlabel('Frequency (GHz)')
plt.ylabel('Magnitude (dB)')
plt.title('Tx Frequency Response Comparison')
plt.legend()
plt.grid(True)
plt.xlim([0, 20])
plt.ylim([-20, 10])
plt.savefig('tx_frequency_comparison.png', dpi=150)
print("Saved: tx_frequency_comparison.png")
```

### Example 2: Channel Simulation

**Goal**: Simulate Tx → Channel → Rx link

```python
#!/usr/bin/env python3
# link_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import lfilter
from pyibisami.ami.model import AMIModel

# Parameters
bit_rate = 10e9
ui = 1.0 / bit_rate
nspui = 32
nbits = 1000
sample_interval = ui / nspui

# Load models
tx_model = AMIModel('./example_tx.dll')
rx_model = AMIModel('./example_rx.dll')

# Generate PRBS (pseudo-random bit sequence)
np.random.seed(42)
bits = np.random.randint(0, 2, nbits)

# Convert bits to NRZ signal
signal = np.repeat(bits * 2 - 1, nspui)  # [-1, +1]

# Initialize Tx (strong pre-emphasis)
tx_params = "(example_tx (preset 3))"
impulse_len = 100 * nspui
impulse_tx = np.zeros(impulse_len)
impulse_tx[0] = 1.0
tx_params_out = tx_model.initialize(impulse_tx, sample_interval, ui, tx_params)

# Process signal through Tx
tx_signal = signal.copy()
tx_clock = np.zeros(len(tx_signal))
tx_model._ami_getwave(tx_signal, len(tx_signal), tx_clock, tx_model._handle)

# Simulate lossy channel (simplified)
# Real channel would come from S-parameters or measurement
channel_loss_db_per_ghz = 2.0  # dB/GHz loss
def channel_response(freq_hz):
    """Frequency-dependent loss."""
    freq_ghz = freq_hz / 1e9
    loss_db = -channel_loss_db_per_ghz * freq_ghz
    return 10 ** (loss_db / 20)

# Apply channel in frequency domain
fft_len = len(tx_signal)
TX_fft = np.fft.rfft(tx_signal, fft_len)
freqs = np.fft.rfftfreq(fft_len, sample_interval)
H_channel = channel_response(freqs)
RX_fft = TX_fft * H_channel
rx_signal_noisy = np.fft.irfft(RX_fft, fft_len)

# Add noise
snr_db = 25
signal_power = np.mean(rx_signal_noisy**2)
noise_power = signal_power / (10 ** (snr_db / 10))
noise = np.random.normal(0, np.sqrt(noise_power), len(rx_signal_noisy))
rx_signal_noisy += noise

# Initialize Rx (CTLE + DFE)
rx_params = "(example_rx (ctle_mode 1) (ctle_mag 6.0) (dfe_mode 2))"
impulse_rx = np.zeros(impulse_len)
impulse_rx[0] = 1.0
rx_params_out = rx_model.initialize(impulse_rx, sample_interval, ui, rx_params)

# Process through Rx
rx_output = rx_signal_noisy.copy()
rx_clock = np.zeros(len(rx_output))
rx_model._ami_getwave(rx_output, len(rx_output), rx_clock, rx_model._handle)

# Sample at clock times to recover bits
clock_samples = rx_clock[rx_clock > 0]  # Non-zero entries are clock times
sampled_indices = (clock_samples / sample_interval).astype(int)
sampled_values = rx_output[sampled_indices]
recovered_bits = (sampled_values > 0).astype(int)

# Calculate BER
bit_errors = np.sum(recovered_bits[:len(bits)] != bits)
ber = bit_errors / len(bits)

print(f"Bit Error Rate: {ber:.2e}")
print(f"Bit Errors: {bit_errors} / {len(bits)}")

# Plot eye diagram
def plot_eye(signal, ui, nspui, ax):
    """Plot eye diagram."""
    samples_per_ui = int(ui / sample_interval)
    eye_traces = signal[:nbits * samples_per_ui].reshape(-1, samples_per_ui)
    time_ui = np.linspace(-0.5, 0.5, samples_per_ui)
    
    for trace in eye_traces:
        ax.plot(time_ui, trace, 'b-', alpha=0.05, linewidth=0.5)
    
    ax.set_xlabel('Time (UI)')
    ax.set_ylabel('Amplitude')
    ax.grid(True)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Tx output
axes[0, 0].plot(tx_signal[:1000] / 1e9, tx_signal[:1000])
axes[0, 0].set_title('Tx Output')
axes[0, 0].set_xlabel('Time (ns)')
axes[0, 0].set_ylabel('Amplitude')

# Channel output (before Rx)
axes[0, 1].plot(rx_signal_noisy[:1000] / 1e9, rx_signal_noisy[:1000])
axes[0, 1].set_title('Channel Output (with noise)')
axes[0, 1].set_xlabel('Time (ns)')
axes[0, 1].set_ylabel('Amplitude')

# Eye at channel output
plot_eye(rx_signal_noisy, ui, nspui, axes[1, 0])
axes[1, 0].set_title('Eye Diagram at Channel Output')

# Eye at Rx output
plot_eye(rx_output, ui, nspui, axes[1, 1])
axes[1, 1].set_title(f'Eye Diagram at Rx Output (BER={ber:.2e})')

plt.tight_layout()
plt.savefig('link_simulation.png', dpi=150)
print("Saved: link_simulation.png")
```

### Example 3: Custom Algorithm (Advanced)

**Goal**: Implement a custom AGC (automatic gain control) in the receiver

**`custom_rx.cpp`**:

```cpp
#include <cmath>
#include "include/ami_rx.h"

class CustomRx : public AmiRx {
    typedef AmiRx inherited;
    
private:
    bool have_agc_;
    double agc_target_;
    double agc_gain_;
    double agc_adapt_rate_;
    
public:
    CustomRx() : have_agc_(false), agc_gain_(1.0) {}
    
    void init(...) override {
        inherited::init(...);
        
        // Read AGC parameters
        std::vector<std::string> node_names;
        
        node_names.push_back("agc_enable");
        have_agc_ = get_param_bool(node_names, false);
        node_names.pop_back();
        
        if (have_agc_) {
            node_names.push_back("agc_target");
            agc_target_ = get_param_float(node_names, 0.5);
            node_names.pop_back();
            
            node_names.push_back("agc_adapt_rate");
            agc_adapt_rate_ = get_param_float(node_names, 0.01);
            node_names.pop_back();
            
            msg_ += "AGC enabled\n";
        }
    }
    
    void proc_sig(double *sig, long len) override {
        // Apply AGC before other processing
        if (have_agc_) {
            apply_agc(sig, len);
        }
        
        // Then apply CTLE, DFE, etc.
        inherited::proc_sig(sig, len);
    }
    
private:
    void apply_agc(double *sig, long len) {
        // Measure signal level (RMS over window)
        const int window_size = 100;
        
        for (long i = 0; i < len; i++) {
            // Apply current gain
            sig[i] *= agc_gain_;
            
            // Adapt gain periodically
            if (i % window_size == 0 && i > 0) {
                // Measure RMS over past window
                double sum_sq = 0.0;
                for (int j = i - window_size; j < i; j++) {
                    sum_sq += sig[j] * sig[j];
                }
                double rms = std::sqrt(sum_sq / window_size);
                
                // Adapt gain to reach target
                double error = agc_target_ - rms;
                agc_gain_ += agc_adapt_rate_ * error * agc_gain_;
                
                // Limit gain range
                if (agc_gain_ < 0.1) agc_gain_ = 0.1;
                if (agc_gain_ > 10.0) agc_gain_ = 10.0;
            }
        }
    }
};

AMIModel *ami_model = new CustomRx();
```

**`custom_rx.py`**:

```python
ami_params = {
    'model': {
        'agc_enable': {
            'type': 'BOOL',
            'usage': 'In',
            'format': 'Value',
            'default': 'False',
            'description': '"Enable automatic gain control"',
        },
        'agc_target': {
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': 0.1,
            'max': 1.0,
            'default': 0.5,
            'description': '"Target RMS amplitude"',
        },
        'agc_adapt_rate': {
            'type': 'FLOAT',
            'usage': 'In',
            'format': 'Range',
            'min': 0.001,
            'max': 0.1,
            'default': 0.01,
            'description': '"AGC adaptation rate"',
        },
        # ... plus CTLE, DFE from base class
    }
}
```

---

## Reference

### IBIS-AMI Standard

**Official specification**: https://ibis.org/
- IBIS Version 7.0 (latest)
- IBIS-AMI Version 7.0

**Key documents**:
- IBIS Modeling Cookbook
- IBIS-AMI Cookbook
- Algorithmic Modeling Interface (AMI) Specification

### PyAMI Resources

**GitHub**: https://github.com/capn-freako/PyAMI
**Documentation**: https://pyibis-ami.readthedocs.io/
**PyPI**: https://pypi.org/project/PyIBIS-AMI/

**Command-line tools**:
- `ami-config`: Generate AMI/IBIS files from Python
- `run-notebook`: Jupyter notebook testing
- `run-tests`: EmPy template testing

### ibisami Resources

**GitHub**: https://github.com/capn-freako/ibisami
**Documentation**: Doxygen-generated (in `doc/` after build)

**Key classes**:
- `AMIModel`: Abstract base
- `AmiTx`: Transmitter base
- `AmiRx`: Receiver base
- `FIRFilter`: FIR filtering
- `DigitalFilter`: IIR filtering
- `DFE`: Decision feedback equalizer

### Signal Processing References

**Books**:
- "Digital Signal Processing" by Mullis & Roberts
- "High-Speed Serial Interface Principles" by Pei-cheng Ku
- "Fundamentals of Digital Communication" by Madhow

**Topics**:
- Pre-emphasis and de-emphasis
- CTLE (Continuous Time Linear Equalizer)
- DFE (Decision Feedback Equalizer)
- CDR (Clock Data Recovery)
- LMS (Least Mean Squares) adaptation

### Development Tools

**C++ compilers**:
- GCC (Linux): `sudo apt-get install g++`
- Clang (macOS): `xcode-select --install`
- MSVC (Windows): Visual Studio or Build Tools

**Python environment**:
```bash
pip install PyIBIS-AMI
```

**Optional tools**:
- Doxygen: C++ documentation generation
- Jupyter: Interactive notebooks
- VSCode: IDE with C++/Python support

### Community

**Mailing lists**:
- IBIS Open Forum: https://www.ibis.org/forum/
- PyBERT discussion: GitHub issues

**Related projects**:
- PyBERT: Complete BERT system with PyAMI
- ibisami-rs: Rust implementation (experimental)

---

## Appendix: Quick Reference

### File Extensions

- `.ami`: AMI parameter file (S-expression format)
- `.ibs`: IBIS model file (component/model definitions)
- `.dll`: Windows dynamic library (compiled model)
- `.so`: Linux shared object (compiled model)
- `.dylib`: macOS dynamic library
- `.py`: Python configuration file
- `.cpp`: C++ implementation file
- `.h`: C++ header file
- `.em`: EmPy template file
- `.ipynb`: Jupyter notebook

### Common Parameters

**Reserved (IBIS-AMI standard)**:
- `AMI_Version`: "5.1", "7.0", etc.
- `Init_Returns_Impulse`: True/False
- `GetWave_Exists`: True/False
- `Ignore_Bits`: Number of bits to ignore
- `Bit_Time`: Unit interval (read-only)
- `Sample_Interval`: Time step (read-only)

**Typical Tx parameters**:
- `tx_tap_*`: Pre-emphasis tap weights
- `pre_cursor`, `post_cursor`: Tap positions
- `amplitude`: Output swing
- `slew_rate`: Edge speed

**Typical Rx parameters**:
- `ctle_mode`, `ctle_freq`, `ctle_mag`: CTLE settings
- `dfe_mode`, `dfe_tap_*`: DFE configuration
- `cdr_mode`: Clock recovery settings
- `agc_enable`: Automatic gain control

### Typical Workflows

**Develop new model**:
1. `cd ibisami/example`
2. Create `my_model.py` (parameters)
3. Create `my_model.cpp` (algorithm)
4. `ami-config my_model.py` (generate files)
5. `make my_model.dll` (compile)
6. `run-notebook my_model.ibs 10e9` (test)

**Modify existing model**:
1. Edit `my_model.py` (change parameters)
2. `ami-config my_model.py` (regenerate)
3. Edit `my_model.cpp` (if algorithm changes)
4. `make my_model.dll` (recompile)
5. Test

**Run parameter sweep**:
1. Create sweep script (Python)
2. Loop over parameter values
3. Call `model.initialize()` with different params
4. Collect and plot results

### Debugging Tips

**C++ debugging**:
```cpp
// Add debug output to msg_
std::ostringstream debug;
debug << "tap_value = " << tap_value << "\n";
msg_ += debug.str();

// Check in Python
params_out = model.initialize(...)
print(params_out)  # Will show debug messages
```

**Python debugging**:
```python
# Enable verbose output
import logging
logging.basicConfig(level=logging.DEBUG)

# Check DLL loading
print(model._dll)
print(model._ami_init)

# Examine arrays
print(f"Impulse: {impulse[:10]}")
print(f"After init: {impulse[:10]}")
```

**Common errors**:
- "DLL not found": Check path, file extension
- "Symbol not found": Model didn't export AMI_Init/GetWave/Close
- "Segmentation fault": Array bounds, null pointer in C++
- "Parameter not found": Mismatch between .ami and .cpp

---

## Summary

The PyAMI and ibisami repositories form a complete ecosystem for IBIS-AMI model development:

**PyAMI provides**:
- Python interface to compiled models (via ctypes)
- Configuration tools (ami-config)
- Testing frameworks (run-notebook, run-tests)
- Parameter parsing and validation
- Analysis and visualization

**ibisami provides**:
- C++ base classes (AMIModel, AmiTx, AmiRx)
- Signal processing algorithms (FIR, IIR, DFE)
- IBIS-AMI API implementation
- Cross-platform build system
- Complete working examples

**Together they enable**:
- Rapid model prototyping (Python config)
- High-performance simulation (C++ algorithms)
- Comprehensive testing (Jupyter notebooks)
- Standards compliance (IBIS-AMI API)
- Easy deployment (single DLL + config files)

**Typical workflow**:
1. Define model in Python (`*.py`)
2. Implement algorithm in C++ (`*.cpp`)
3. Generate config files (ami-config)
4. Compile to DLL (make)
5. Test with Python (run-notebook)
6. Deploy to simulators

This architecture separates concerns, maximizes code reuse, and provides a smooth development experience from prototyping to production.
