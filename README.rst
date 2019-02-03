Calculate convolutional neural network layer sizes and receptive fields.


Usage
================================================================================

To calculate the output size and receptive fields for a convnet specfied by the
*layers.yaml* file:

.. code-block:: bash

    cnncalc --input-size 256 layers.yaml


The convnet structure can also be read from stdin, in which case the format is
assumed to by yaml.  The following calculates the output sizes and receptive
fields for a two layer network.

.. code-block:: bash

    cnncalc --input-size 256 -
    - kernel_size: 3
    - {kernel_size: 3, stride: 2}
    <ctrl+d>


Convnet Schema
================================================================================

A convnet is defined by a list of layer objects where each layer has the
following properties:

    - type: string - 'conv' or 'pool' (defaults to 'conv')
    - padding: string - 'valid' or 'same' (defaults to 'same')
    - kernel_size: integer - size of filter kernel
    - stride: integer - stride as a single integer


Convnets are specified using yaml or json.  Here is yaml code specifying a
convnet consisting of three convolutional layers and a single pooling layer.

.. code-block:: yaml

    - kernel_size: 3
    - {kernel_size: 3, stride: 2}
    - {kernel_size: 3, padding: valid}
    - {type: pool, kernel_size: 2}


The input size is provided with the ``--input-size`` option.  Alternatively, it
can be given in convnet definition by setting the top-level ``input_size``
property and assigning the list of layers to the top-level ``layers`` property.


The example given above including the input size is

.. code-block:: yaml

    input_size: 128
    layers:
        - kernel_size: 3
        - {kernel_size: 3, stride: 2}
        - {kernel_size: 3, padding: valid}
        - {type: pool, kernel_size: 2}



