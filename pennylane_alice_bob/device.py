"""
This module contains the AliceBobQubitDevice class. It constructs custom devices for PennyLane,
using either local or remote backends provided by Alice & Bob.
"""

import warnings
import pennylane as qml
from pennylane import DeviceError
from qiskit_alice_bob_provider.local.provider import AliceBobLocalProvider
from qiskit_alice_bob_provider import AliceBobRemoteProvider

class AliceBobQubitDevice(qml.devices.Device):
    """
    Alice & Bob's custom device for PennyLane.
    
    This device allows for the simulation of quantum circuits using Alice & Bob's custom backends.
    """

    @property
    def name(self):
        """The name of the device."""
        return "alicebob.qubit"
    # name = "Alice & Bob's custom PennyLane plugin"
    # short_name = "alicebob.qubit"
    # pennylane_requires = ">=0.28.0"
    # version = "0.0.1"
    # author = "QuantumETS"

    @staticmethod
    def configured_backend(backend, api_key='', **kwargs):
        """
        Configures and returns the specified backend.

        Parameters:
        - backend (str): The name of the backend to use.
        - api_key (str, optional): The API key for remote access. Defaults to ''.
        - **kwargs: Arbitrary keyword arguments for backend configuration (kappa_1, kappa_2, ...).
        
        Returns:
        - The configured backend.
        """
        for element in AliceBobLocalProvider().backends():
            if backend.strip() == element.name.strip():
                print(f"Using alice & bob {backend} backend...")
                if len(api_key) > 1:
                    return AliceBobRemoteProvider(api_key).get_backend(backend, **kwargs)
                else:
                    return AliceBobLocalProvider().get_backend(backend, **kwargs)
        
        warnings.warn(f"Backend '{backend}' not found. Using default local backend.")
        return AliceBobLocalProvider().get_backend('default', **kwargs)

    def __new__(self, wires=1, shots=1024, seed="global", max_workers=None, alice_backend="EMU:6Q:PHYSICAL_CATS", api_token="", **kwargs):
        """
        Creates a new instance or reuses an existing instance of the AliceBobQubitDevice.

        Parameters:
        - wires (int, optional): The number of wires. Defaults to 1.
        - shots (int, optional): The number of shots. Defaults to 1024.
        - seed (str, optional): The seed for random number generators. Defaults to "global".
        - max_workers (int, optional): The maximum number of workers. Defaults to None.
        - alice_backend (str, optional): The backend to use. Defaults to "EMU:6Q:PHYSICAL_CATS".
        - api_token (str, optional): The API token for remote access. Defaults to "".

        Returns:
        - An instance of qml.Device configured with the specified backend.
        """
        provider = self.configured_backend(alice_backend, api_token, **kwargs)

        class Stub:
            n_qubits = wires

        def conf():
            return Stub()

        provider.configuration = conf

        if provider is None:
            backend_names = " ".join(element.name for element in AliceBobLocalProvider().backends())
            raise DeviceError(f"Backend error, please choose one of the following: {backend_names}")
        
        return qml.device('qiskit.remote', wires=wires, backend=provider, shots=shots)
