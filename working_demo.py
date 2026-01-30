#!/usr/bin/env python3
"""
WORKING PyAMI Demo - Actually Shows Pre-Emphasis!
This version correctly configures the model and shows real signal processing.
"""

import numpy as np
import matplotlib.pyplot as plt
from ctypes import c_double
from pyibisami.ami.model import AMIModel, AMIModelInitializer

def demo_preemphasis():
    """Demonstrates transmitter pre-emphasis with different tap configurations"""
    
    print("=" * 70)
    print("PyAMI Working Demo - Transmitter Pre-Emphasis")
    print("=" * 70)
    
    # Load the model
    dll_path = r"tests\examples\example_tx_x86_amd64.dll"
    print(f"\nLoading model: {dll_path}")
    model = AMIModel(dll_path)
    print("✓ Model loaded\n")
    
    # Simulation parameters
    bit_rate = 10e9
    ui = 1.0 / bit_rate
    nspui = 32
    sample_interval = ui / nspui
    
    print(f"Simulation: {bit_rate/1e9:.0f} Gbps, {nspui} samples/UI")
    print(f"Sample interval: {sample_interval*1e12:.2f} ps\n")
    
    # Test different tap configurations
    configs = [
        {
            "name": "No Pre-emphasis (All on Main Tap)",
            "tx_tap_np1": 0,  # Pre-cursor
            "tx_tap_nm1": 0,  # Post-cursor 1
            "tx_tap_nm2": 0,  # Post-cursor 2
        },
        {
            "name": "Light Pre-emphasis",
            "tx_tap_np1": 2,
            "tx_tap_nm1": 3,
            "tx_tap_nm2": 1,
        },
        {
            "name": "Medium Pre-emphasis",
            "tx_tap_np1": 4,
            "tx_tap_nm1": 8,
            "tx_tap_nm2": 3,
        },
        {
            "name": "Strong Pre-emphasis",
            "tx_tap_np1": 6,
            "tx_tap_nm1": 12,
            "tx_tap_nm2": 5,
        }
    ]
    
    results = []
    
    for config in configs:
        print(f"Testing: {config['name']}")
        print(f"  Taps: np1={config['tx_tap_np1']}, nm1={config['tx_tap_nm1']}, nm2={config['tx_tap_nm2']}")
        
        # Create channel impulse (ideal)
        impulse_len = 200 * nspui
        impulse_response = np.zeros(impulse_len)
        impulse_response[0] = 1.0
        channel_response = (c_double * impulse_len)(*impulse_response)
        
        # Configure AMI parameters (CORRECT FORMAT!)
        ami_params = {
            "root_name": "example_tx",  # ← CRITICAL: Must match model name!
            "tx_tap_units": 27,         # Total current available
            "tx_tap_np1": config["tx_tap_np1"],
            "tx_tap_nm1": config["tx_tap_nm1"],
            "tx_tap_nm2": config["tx_tap_nm2"]
        }
        
        # Initialize
        init_data = {
            "channel_response": channel_response,
            "row_size": impulse_len,
            "num_aggressors": 0,
            "sample_interval": c_double(sample_interval),
            "bit_time": c_double(ui)
        }
        
        initializer = AMIModelInitializer(ami_params, **init_data)
        model.initialize(initializer)
        
        # Get result
        impulse_out = np.array(model._initOut[:impulse_len])
        
        # Analyze
        main_idx = np.argmax(np.abs(impulse_out))
        main_amp = impulse_out[main_idx]
        pre_tap = impulse_out[main_idx - nspui] if main_idx >= nspui else 0
        post1 = impulse_out[main_idx + nspui] if main_idx + nspui < impulse_len else 0
        post2 = impulse_out[main_idx + 2*nspui] if main_idx + 2*nspui < impulse_len else 0
        
        print(f"  Main tap: {main_amp:.4f} at sample {main_idx}")
        print(f"  Pre-tap:  {pre_tap:.4f}")
        print(f"  Post-1:   {post1:.4f}")
        print(f"  Post-2:   {post2:.4f}")
        print(f"  Model says: {model.msg.decode('utf-8').strip()}")
        print()
        
        results.append({
            "name": config["name"],
            "signal": impulse_out,
            "main": main_idx
        })
    
    # Plot all results
    print("Generating comparison plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    time_ns = np.arange(impulse_len) * sample_interval * 1e9
    
    for i, result in enumerate(results):
        ax = axes[i]
        signal = result["signal"]
        main_idx = result["main"]
        
        # Time domain (zoom to first 5 ns)
        ax.plot(time_ns, signal, linewidth=1.5, color=f'C{i}')
        ax.axvline(main_idx * sample_interval * 1e9, color='red', 
                   linestyle='--', alpha=0.5, label='Main tap')
        ax.axhline(0, color='gray', linestyle='-', alpha=0.3)
        
        # Mark cursor positions
        ax.plot(main_idx * sample_interval * 1e9, signal[main_idx], 
                'ro', markersize=8, label='Main')
        if main_idx >= nspui:
            ax.plot((main_idx - nspui) * sample_interval * 1e9, 
                   signal[main_idx - nspui], 'gs', markersize=8, label='Pre')
        if main_idx + nspui < impulse_len:
            ax.plot((main_idx + nspui) * sample_interval * 1e9,
                   signal[main_idx + nspui], 'b^', markersize=8, label='Post-1')
        
        ax.set_xlim([0, 5])
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('Amplitude')
        ax.set_title(result["name"], fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('working_demo_output.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: working_demo_output.png")
    
    # Frequency response comparison
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    fft_len = 4096
    freq_ghz = np.fft.rfftfreq(fft_len, sample_interval) / 1e9
    
    for i, result in enumerate(results):
        H = np.fft.rfft(result["signal"], fft_len)
        H_dB = 20 * np.log10(np.abs(H) + 1e-12)
        ax.plot(freq_ghz, H_dB, linewidth=2, label=result["name"], color=f'C{i}')
    
    ax.set_xlabel('Frequency (GHz)', fontsize=12)
    ax.set_ylabel('Magnitude (dB)', fontsize=12)
    ax.set_title('Frequency Response: Effect of Pre-Emphasis', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_xlim([0, 20])
    ax.set_ylim([-30, 15])
    
    # Annotate
    ax.text(15, 8, 'Pre-emphasis boosts\nhigh frequencies', 
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
            fontsize=10)
    
    plt.tight_layout()
    plt.savefig('frequency_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: frequency_comparison.png")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\n📊 What You're Seeing:")
    print("  • Time domain: Multi-tap FIR filter responses")
    print("  • Main tap carries most signal energy")
    print("  • Pre/post-cursors create controlled ISI (de-emphasis)")
    print("  • Frequency domain: High-frequency boost compensates for channel loss")
    print("\n💡 Key Insight:")
    print("  The transmitter intentionally distorts the signal!")
    print("  When this passes through a lossy channel, it arrives clean.")
    print("\n📁 Output files:")
    print("  - working_demo_output.png (time domain comparison)")
    print("  - frequency_comparison.png (frequency response)")

if __name__ == "__main__":
    demo_preemphasis()
