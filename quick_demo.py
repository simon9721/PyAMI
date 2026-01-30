#!/usr/bin/env python3
"""
Quick PyAMI Demo
Shows how to load and test an IBIS-AMI model
"""

import numpy as np
import matplotlib.pyplot as plt
from ctypes import c_double
from pyibisami.ami.model import AMIModel, AMIModelInitializer

def demo_ami_model():
    """Test the example_tx model"""
    
    print("=" * 60)
    print("PyAMI Quick Demo")
    print("=" * 60)
    
    # 1. Load the model DLL
    dll_path = r"tests\examples\example_tx_x86_amd64.dll"
    print(f"\n1. Loading model: {dll_path}")
    
    try:
        model = AMIModel(dll_path)
        print("   ✓ Model loaded successfully!")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 2. Set up simulation parameters
    bit_rate = 10e9  # 10 Gbps
    ui = 1.0 / bit_rate  # Unit interval (100 ps)
    nspui = 32  # Samples per UI
    sample_interval = ui / nspui
    
    print(f"\n2. Simulation Parameters:")
    print(f"   Bit rate: {bit_rate/1e9:.1f} Gbps")
    print(f"   Unit Interval: {ui*1e12:.1f} ps")
    print(f"   Samples per UI: {nspui}")
    print(f"   Sample interval: {sample_interval*1e12:.2f} ps")
    
    # 3. Create impulse input (channel response)
    impulse_len = 200 * nspui  # 200 UI long
    impulse_response = np.zeros(impulse_len)
    impulse_response[0] = 1.0  # Ideal impulse at start
    
    print(f"\n3. Created channel impulse response:")
    print(f"   Length: {impulse_len} samples ({impulse_len/nspui:.0f} UI)")
    print(f"   Type: Ideal impulse (delta function)")
    
    # Convert to ctypes array
    channel_response = (c_double * impulse_len)(*impulse_response)
    
    # 4. Set up AMI parameters (using correct parameter names!)
    ami_params = {
        "example_tx": {
            "tx_tap_units": 27,  # Total current available (max)
            "tx_tap_np1": 4,     # Pre-cursor tap (de-emphasis)
            "tx_tap_nm1": 8,     # Post-cursor tap 1 (de-emphasis) 
            "tx_tap_nm2": 3      # Post-cursor tap 2 (de-emphasis)
        }
    }
    
    print(f"\n4. AMI Parameters:")
    print(f"   Model: example_tx")
    print(f"   tx_tap_units: {ami_params['example_tx']['tx_tap_units']} (total current)")
    print(f"   tx_tap_np1: {ami_params['example_tx']['tx_tap_np1']} (pre-cursor)")
    print(f"   tx_tap_nm1: {ami_params['example_tx']['tx_tap_nm1']} (post-cursor 1)")
    print(f"   tx_tap_nm2: {ami_params['example_tx']['tx_tap_nm2']} (post-cursor 2)")
    
    # 5. Create initializer object
    print(f"\n5. Creating model initializer...")
    init_data = {
        "channel_response": channel_response,
        "row_size": impulse_len,
        "num_aggressors": 0,
        "sample_interval": c_double(sample_interval),
        "bit_time": c_double(ui)
    }
    
    try:
        initializer = AMIModelInitializer(ami_params, **init_data)
        print("   ✓ Initializer created!")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 6. Initialize model
    print(f"\n6. Initializing model...")
    try:
        model.initialize(initializer)
        print("   ✓ Model initialized!")
        
        # Get the output impulse response
        impulse_out = np.array(model._initOut[:impulse_len])
        
        # Show returned parameters
        if hasattr(model, '_ami_params_out'):
            print(f"\n   Returned parameters:")
            params_str = str(model._ami_params_out)
            if len(params_str) > 200:
                print(f"   {params_str[:200]}...")
            else:
                print(f"   {params_str}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 7. Analyze results
    print(f"\n7. Results:")
    main_cursor = np.argmax(np.abs(impulse_out))
    print(f"   Main cursor at sample: {main_cursor}")
    print(f"   Main cursor amplitude: {impulse_out[main_cursor]:.4f}")
    
    # Find pre-cursor and post-cursor taps
    precursor = impulse_out[main_cursor - nspui] if main_cursor >= nspui else 0
    postcursor1 = impulse_out[main_cursor + nspui] if main_cursor + nspui < len(impulse_out) else 0
    postcursor2 = impulse_out[main_cursor + 2*nspui] if main_cursor + 2*nspui < len(impulse_out) else 0
    
    print(f"   Pre-cursor tap: {precursor:.4f}")
    print(f"   Post-cursor tap 1: {postcursor1:.4f}")
    print(f"   Post-cursor tap 2: {postcursor2:.4f}")
    
    # 8. Plot results
    print(f"\n8. Generating plots...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Time domain
    time_ns = np.arange(len(impulse_out)) * sample_interval * 1e9
    ax1.plot(time_ns, impulse_out, linewidth=1.5)
    ax1.axvline(main_cursor * sample_interval * 1e9, color='r', linestyle='--', 
                alpha=0.5, label='Main cursor')
    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Transmitter Impulse Response (Time Domain)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim([0, 20])  # Show first 20 ns
    
    # Frequency domain
    fft_len = 4096
    H = np.fft.rfft(impulse_out, fft_len)
    freq_ghz = np.fft.rfftfreq(fft_len, sample_interval) / 1e9
    H_dB = 20 * np.log10(np.abs(H) + 1e-12)
    
    ax2.plot(freq_ghz, H_dB, linewidth=1.5)
    ax2.set_xlabel('Frequency (GHz)')
    ax2.set_ylabel('Magnitude (dB)')
    ax2.set_title('Transmitter Frequency Response')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 20])
    ax2.set_ylim([-40, 10])
    
    plt.tight_layout()
    output_file = 'pyami_demo_output.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"   ✓ Plot saved: {output_file}")
    
    # Don't show plot interactively (may block)
    # plt.show()
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nWhat just happened:")
    print("1. Loaded an IBIS-AMI transmitter model (DLL)")
    print("2. Fed it an ideal channel impulse (delta function)")
    print("3. Model applied transmitter pre-emphasis")
    print("4. Output shows how Tx shapes the signal:")
    print("   - Main tap: strongest part of signal")
    print("   - Pre/post-cursor taps: intentional distortion")
    print("   - This compensates for channel losses")
    print("\nThe frequency response shows high-frequency boost")
    print("(pre-emphasis) to counteract channel attenuation.")
    print(f"\nCheck the plot: {output_file}")

if __name__ == "__main__":
    demo_ami_model()
