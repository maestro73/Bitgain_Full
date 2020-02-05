# BitGain 

Predict bitcoin value for the next 9minutes, with Recurrental Neural Network GRU.
<br />
<h1>Requirements:</h1>
<br/>

<ul>
<li>Python3</li>
<li><a href="http://keras.io/">Keras 2</a></li>
<li><a href="http://www.numpy.org/">numpy</a></li>
<li><a href="http://matplotlib.org/">MatploitLib</a></li>
</ul>
<br />
<h1>Instructions</h1>
<br />
<br />
<b>Training on new data:</b><br />
<code>python3 network.py -train <i>dataset_path</i> -iterations <i>number_of_training_iterations</i></code>
<p>To finetune the new model with an old one just add <code>-finetune <i>base_model_path</i></code> to the line above.</p>
<p>At the end of the training you will have an updated model.h5 with the new weights and you will see a plot with the test results.</p>
<br />
<b>Running:</b><br />
<code>python3 network.py -run <i>dataset_path</i> -model <i>model_path</i></code>
<p>The dataset is also required when you run, to perform normalization.</p>
<p>To visualize a plot with the real and predicted results enter Crtl-C and type no ,the program will create chart.png with the results.</p>

<br/>
Working example with <a href="https://github.com/findingnino/Bitgain/blob/master/model_1250_2018-01-01.h5">this model</a>:
<br/>
(Red:Predicted,Green:Real values)
<img src="https://github.com/findingnino/Bitgain/blob/master/chart_run_2018-01-01.png" />
