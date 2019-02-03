#!/usr/bin/env python
#!  pylint: disable=missing-docstring

import argparse
import sys


COLUMN_HEADERS = ['Layer', 'Output Size', 'Receptive Field']
COLUMN_WIDTHS = [None, 12, 16]
COLUMN_ATTRIBUTES = ['description', 'output_size', 'receptive_field_size']
COLUMN_ALIGNS = ['<', '^', '^']
COLUMN_SEPERATOR = ' | '
HORIZONTAL_RULE_CHARACTER = '-'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'config',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
    )

    parser.add_argument(
        '--parse-only',
        action='store_true',
    )

    parser.add_argument(
        '--input-size',
        type=int,
        default=None,
    )

    args = parser.parse_args()

    config = load_config(args.config)
    if config:
        if args.parse_only:
            import pprint
            pprint.pprint(config)
        else:
            layers = build_layers_from_config(config, input_size=args.input_size)

            previous_layer = layers[0]
            for layer in layers[1:]:
                layer.calculate(previous_layer)
                previous_layer = layer

            print(build_output_table(layers))




def load_config(config):
    if config.name.endswith('.yaml'):
        import yaml
        config = yaml.load(config)
    elif config.name.endswith('.json'):
        import json
        config = json.load(config)
    elif config.name == '<stdin>':
        try:
            import yaml
            config = yaml.load(config)
        except Exception as yaml_error: #!  pylint: disable=broad-except
            try:
                import json
                config = json.load(config)
            except Exception as json_error:
                raise json_error from yaml_error

    return config


def build_layers_from_config(config, input_size):
    #   if config is a list it is assumed to be a list of layer configs
    #   otherwise, config is a mapping where 'layers' is mapped to the list of
    #   layer configs and optionally 'input_size' gives the input layer size
    if isinstance(config, list):
        layers = [Input(input_size)]
    else:
        layers = [Input(config.get('input_size', input_size))]
        config = config.get('layers', list())

    layers.extend(create_layer_from_config(layer) for layer in config)

    return layers


def create_layer_from_config(config):
    layer_type = config.get('type', 'conv').lower()

    #   use shortcuts/abbreviations for kernel_size
    if 'kernel_size' in config:
        pass
    elif 'kernel' in config:
        config['kernel_size'] = config['kernel']
    elif 'k' in config:
        config['kernel_size'] = config['k']

    #   use shortcuts/abbreviations for stride
    if 'stride' not in config and 's' in config:
        config['stride'] = config['s']

    #   use shortcuts/abbreviations for padding
    if 'padding' not in config and 'p' in config:
        config['padding'] = config['p']

    if layer_type == 'conv':
        layer = Conv(kernel=config['kernel_size'],
                     stride=config.get('stride', 1),
                     padding=config.get('padding', 'same'),
                     name=config.get('name'))
    elif layer_type == 'pool':
        layer = Pool(size=config['kernel_size'],
                     name=config.get('name'))

    return layer


def build_output_table(layers):
    #   calculate widths for columns with missing column width entries
    for i, (attribute, width) in enumerate(zip(COLUMN_ATTRIBUTES, COLUMN_WIDTHS)):
        if width is None:
            COLUMN_WIDTHS[i] = max(len(str(getattr(layer, attribute))) for layer in layers)

    header = COLUMN_SEPERATOR.join(
        f'{header:{width}}' for header, width in zip(COLUMN_HEADERS, COLUMN_WIDTHS)
    )

    rows = [
        COLUMN_SEPERATOR.join(
            f'{getattr(layer, attribute):{align}{width}}'
            for attribute, align, width in zip(COLUMN_ATTRIBUTES, COLUMN_ALIGNS, COLUMN_WIDTHS)
        )
        for layer in layers
    ]

    horizontal_rule = HORIZONTAL_RULE_CHARACTER * max(len(header), max(len(row) for row in rows))

    return '\n'.join([
        header,
        horizontal_rule,
        *rows,
        horizontal_rule
    ])




class Layer:
    #!  pylint: disable=missing-docstring
    def __init__(self, name=None):
        self.name = name
        self.output_size = None
        self.receptive_field_size = None
        self.receptive_field_center = None
        self.jump = 1


    def __str__(self):
        return self.description


    @property
    def description(self):
        description = self.__class__.__name__

        if self.name:
            description += self.name

        return description




class Input(Layer):
    #!  pylint: disable=missing-docstring
    def __init__(self, size, name=None):
        super().__init__(name)
        self.output_size = size
        self.receptive_field_size = 1
        self.receptive_field_center = 0.5
        self.jump = 1




class Conv(Layer):
    #!  pylint: disable=missing-docstring
    def __init__(self, kernel, stride=1, padding='same', name=None):
        super().__init__(name)
        if padding == 'same':
            self._padding = padding
            padding = kernel // 2
        elif padding == 'valid':
            self._padding = padding
            padding = 0
        else:
            self._padding = None

        self.kernel = kernel
        self.padding = padding
        self.stride = stride


    @property
    def description(self):
        return super().description + (
            f' ['
            f'kernel_size={self.kernel}, '
            f'stride={self.stride}, '
            f'padding={self.padding}{f"({self._padding})" if self._padding else ""}'
            f']'
        )


    def calculate(self, input_layer):
        self.output_size = self.calculate_output_size(input_layer.output_size)
        self.receptive_field_size = self.calculate_receptive_field_size(
            input_layer.receptive_field_size,
            input_layer.jump,
        )
        self.receptive_field_center = self.calculate_receptive_field_center(
            input_layer.receptive_field_center,
            input_layer.jump,
        )
        self.jump = self.calculate_output_jump(input_layer.jump)


    def calculate_output_size(self, input_size):
        return (self.kernel % 2) + ((input_size + 2 * self.padding - self.kernel) // self.stride)


    def calculate_output_jump(self, input_jump):
        return input_jump * self.stride


    def calculate_receptive_field_size(self, input_receptive_field, input_jump):
        return input_receptive_field + (self.kernel - 1) * input_jump


    def calculate_receptive_field_center(self, input_receptive_center, input_jump):
        return input_receptive_center + ((self.kernel - 1) // 2 - self.padding) * input_jump




class Pool(Conv):
    #!  pylint: disable=missing-docstring
    def __init__(self, size, name=None):
        super().__init__(size, stride=size, name=name)




if __name__ == '__main__':
    main()




