# Import modules
import csv
import numpy as np
import nengo
import nengo_spinnaker

# Import classes
from nengo.processes import WhiteNoise
from nengo_spinnaker.utils import profiling

# Parameters to profile
dimensions = 1
ensemble_size = 200

model = nengo.Network()
with model:
    # Create standard communication channel network with white noise input
    inp = nengo.Node(WhiteNoise(), label="inp")
    inp_p = nengo.Probe(inp)

    pre = nengo.Ensemble(ensemble_size, dimensions=dimensions, label="pre")
    pre_p = nengo.Probe(pre, synapse=0.01)
    nengo.Connection(inp, pre)
    
    post = nengo.Ensemble(ensemble_size, dimensions=dimensions, label="post")
    posts_p = nengo.Probe(post, synapse = 0.01)
    nengo.Connection(pre, post,
                     function=lambda x: np.random.random(dimensions))
    
    # Setup SpiNNaker-specific options to supply white noise from on
    # chip and profile the ensemble at the start of the channel
    nengo_spinnaker.add_spinnaker_params(model.config)
    model.config[inp].function_of_time = True
    model.config[pre].profile = True

    # Create a SpiNNaker simulator and run model
    sim = nengo_spinnaker.Simulator(model)
    with sim:
        sim.run(10.0)

    # Read profiler data
    profiler_data = sim.profiler_data[pre]

    # Open CSV file and create writer
    with open("profile_communication_channel.csv", "wb") as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write header row for CSV with extra columns
        # for number of neurons and dimensions
        profiling.write_csv_header(profiler_data, csv_writer,
                                   ["Num neurons", "Dimensions"])

        # Write a row from the profiler data dollo
        profiling.write_csv_row(profiler_data, csv_writer,
                                [ensemble_size, dimensions])