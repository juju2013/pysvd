import re

import svd.type
import svd.classes

# /device
# http://www.keil.com/pack/doc/cmsis/svd/html/elem_device.html

class device(svd.classes.base):
    '''The element <device> provides the outermost frame of the description.'''

    def __init__(self, node):
        svd.classes.base.__init__(self, node)

        attr = {}
        attr['schema_version'] = svd.parser.text(svd.node.attribute(node, 'schemaVersion', True))

        attr['vendor'] = svd.parser.text(svd.node.element(node, 'vendor'))
        attr['vendor_id'] = svd.parser.text(svd.node.element(node, 'vendorID'))
        attr['name'] = svd.parser.text(svd.node.element(node, 'name', True))
        attr['series'] = svd.parser.text(svd.node.element(node, 'series'))
        attr['version'] = svd.parser.text(svd.node.element(node, 'version', True))
        attr['description'] = svd.parser.text(svd.node.element(node, 'description', True))
        license_text = svd.parser.text(svd.node.element(node, 'licenseText'))
        attr['header_system_filename'] = svd.parser.text(svd.node.element(node, 'headerSystemFilename'))
        attr['header_definitions_prefix'] = svd.parser.text(svd.node.element(node, 'headerDefinitionsPrefix'))
        attr['address_unit_bits'] = svd.parser.integer(svd.node.element(node, 'addressUnitBits', True))
        attr['width'] = svd.parser.integer(svd.node.element(node, 'width', True))

        # property group
        attr['size'] = svd.parser.integer(svd.node.element(node, 'size'), 32)
        attr['access'] = svd.parser.enum(svd.type.access, svd.node.element(node, 'access'), svd.type.access.read_write)
        attr['protection'] = svd.parser.enum(svd.type.protection, svd.node.element(node, 'protection'), svd.type.protection.none)
        attr['reset_value'] = svd.parser.integer(svd.node.element(node, 'resetValue'), 0x00000000)
        attr['reset_mask'] = svd.parser.integer(svd.node.element(node, 'resetMask'), 0xFFFFFFFF)

        # Clean up license text from whitespaces
        result = ''
        for line in license_text.splitlines():
            line = line.strip()
            if len(line):
                result += line + '\n'
        attr['license_text'] = result
        self.add_attributes(attr)

        cpu = node.find('cpu')
        if cpu is not None:
            self.cpu = svd.element.cpu(self, cpu)

        peripherals = node.find('peripherals')
        if peripherals is None:
            raise SyntaxError("No element 'peripherals' found in 'device'")

        self.peripheral = []
        peripheral.add_elements(self, self.peripheral, peripherals, 'peripheral')

# /device/cpu

class cpu(svd.classes.parent):
    '''The CPU section describes the processor included in the microcontroller device.'''

    def __init__(self, parent, node):
        svd.classes.parent.__init__(self, parent, node)

        attr = {}
        attr['name'] = svd.parser.enum(svd.type.cpuName, svd.node.element(node, 'name', True).replace('+', 'PLUS'))
        attr['revision'] = svd.parser.text(svd.node.element(node, 'revision', True))
        attr['endian'] = svd.parser.enum(svd.type.endian, svd.node.element(node, 'endian', True))
        attr['mpu_present'] = svd.parser.boolean(svd.node.element(node, 'mpuPresent', True))
        attr['fpu_present'] = svd.parser.boolean(svd.node.element(node, 'fpuPresent', True))

        attr['fpu_dp'] = svd.parser.boolean(svd.node.element(node, 'fpuDP'))
        attr['icache_present'] = svd.parser.boolean(svd.node.element(node, 'icachePresent'))
        attr['dcache_present'] = svd.parser.boolean(svd.node.element(node, 'dcachePresent'))
        attr['itcm_present'] = svd.parser.boolean(svd.node.element(node, 'itcmPresent'))
        attr['dtcm_present'] = svd.parser.boolean(svd.node.element(node, 'dtcmPresent'))
        attr['vtor_present'] = svd.parser.boolean(svd.node.element(node, 'vtorPresent'), True)

        attr['nvic_prio_bits'] = svd.parser.integer(svd.node.element(node, 'nvicPrioBits', True))
        attr['vendor_systick_config'] = svd.parser.boolean(svd.node.element(node, 'vendorSystickConfig', True))

        attr['device_num_interrupts'] = svd.parser.integer(svd.node.element(node, 'deviceNumInterrupts'))
        attr['sau_num_regions'] = svd.parser.integer(svd.node.element(node, 'sauNumRegions'))
        self.add_attributes(attr)

        child = node.find('sauRegionsConfig')
        if child is not None:
            self.sau_regions_config = sau_region_config(self, child)

class sauRegionConfig(svd.classes.group):
    '''Set the configuration for the Secure Attribution Unit (SAU) when they are preconfigured by HW or Firmware.'''

    attributes = ['protection']

    def __init__(self, parent, node):
        svd.classes.group.__init__(self, parent, node)

        attr = {}
        attr['enabled'] = svd.parser.boolean(svd.node.attribute(node, 'enabled'))
        attr['protection'] = svd.parser.enum(svd.type.protection, svd.node.element(node, 'protectionWhenDisabled'))
        self.add_attributes(attr)

        self.region = []
        for child in node.findall('region'):
            self.region.append( sau_regions_config_region(self, child) )

class sau_regions_config_region(svd.classes.parent):
    '''Define the regions of the Secure Attribution Unit (SAU)'''

    def __init__(self, parent, node):
        svd.classes.parent.__init__(self, parent, node)

        attr = {}
        attr['enabled'] = svd.parser.boolean(svd.node.attribute(node, 'enabled'), True)
        attr['name'] = svd.parser.text(svd.node.attribute(node, 'name'))

        attr['base'] = svd.parser.integer(svd.node.element(node, 'base', True))
        attr['limit'] = svd.parser.integer(svd.node.element(node, 'limit', True))
        attr['access'] = svd.parser.enum(svd.type.region_access, svd.node.element(node, 'access', True))
        self.add_attributes(attr)

# /device/peripherals

class peripherals(svd.classes.parent):
    '''All peripherals of a device are enclosed within the tag <peripherals>.'''

    def __init__(self, parent, node):
        if parent is not None and not isinstance(parent, device):
            raise TypeError("Only parent 'device' allowed")
        svd.classes.parent.__init__(self, parent, node)

        self.peripheral = []
        peripheral.add_elements(self, self.peripheral, node, 'peripheral')

        if len(self.peripheral) < 1:
            raise SyntaxError("At least one element of 'peripheral' is mandatory in 'peripherals'")

class peripheral(svd.classes.dim):
    '''At least one peripheral has to be defined.'''

    def __init__(self, parent, node, name = None, offset = 0):
        if parent is not None and not isinstance(parent, device):
            raise TypeError("Only parent 'device' allowed")
        svd.classes.dim.__init__(self, parent, node, name, offset)

        attr = {}
        attr['version'] = svd.parser.text(svd.node.element(node, 'version'))
        attr['alternate_peripheral'] = svd.parser.text(svd.node.element(node, 'alternatePeripheral'))
        attr['group_name'] = svd.parser.text(svd.node.element(node, 'groupName'))
        attr['prepend_to_name'] = svd.parser.text(svd.node.element(node, 'prependToName'))
        attr['append_to_name'] = svd.parser.text(svd.node.element(node, 'appendToName'))
        attr['header_struct_name'] = svd.parser.text(svd.node.element(node, 'headerStructName'))
        attr['disable_condition'] = svd.parser.text(svd.node.element(node, 'disableCondition'))
        attr['base_address'] = svd.parser.integer(svd.node.element(node, 'baseAddress', True))

        self.add_attributes(attr)

class address_block(svd.classes.group):
    '''Specify an address range uniquely mapped to this peripheral'''

    attributes = ['protection']

    def __init__(self, parent, node):
        svd.classes.group.__init__(self, parent, node)

        attr = {}
        attr['offset'] = svd.parser.integer(svd.node.element(node, 'offset', True))
        attr['size'] = svd.parser.integer(svd.node.element(node, 'size', True))
        attr['usage'] = svd.parser.enum(svd.type.usage, svd.node.element(node, 'usage', True))
        attr['protection'] = svd.parser.enum(svd.type.protection, svd.node.element(node, 'protection'))
        self.add_attributes(attr)

class interrupt(svd.classes.parent):
    '''A peripheral can have multiple interrupts'''

    def __init__(self, parent, node):
        svd.classes.parent.__init__(self, parent, node)

        attr = {}
        attr['name'] = svd.parser.text(svd.node.element(node, 'name', True))
        attr['description'] = svd.parser.text(svd.node.element(node, 'description'))
        attr['value'] = svd.parser.integer(svd.node.element(node, 'value', True))
        self.add_attributes(attr)

# /device/peripherals/registers

class write_constraint(svd.classes.parent):
    '''Define constraints for writing values to a field. You can choose between three options, which are mutualy exclusive.'''

    def __init__(self, parent, node):
        svd.classes.parent.__init__(self, parent, node)

        attr = {}
        write_as_read = svd.node.element(node, 'writeAsRead')
        use_enumerated_values = svd.node.element(node, 'useEnumeratedValues')
        range_node = node.find("./range")
        if write_as_read is not None:
            attr['write_as_read'] = svd.parser.boolean(write_as_read)
        elif use_enumerated_values is not None:
            attr['use_enumerated_values'] = svd.parser.boolean(use_enumerated_values)
        else:
            range_minimum = None
            range_maximum = None
            if range_node is not None:
                range_minimum = svd.node.element(range_node, 'minimum')
                range_maximum = svd.node.element(range_node, 'maximum')

            if range_minimum is None or range_maximum is None:
                raise SyntaxError("Either 'writeAsRead', 'useEnumeratedValues' or 'range' is mandatory in 'writeConstraint'")

            attr['range_minimum'] = svd.parser.integer(range_minimum)
            attr['range_maximum'] = svd.parser.integer(range_maximum)

        self.add_attributes(attr)

class fields(svd.classes.parent):
    '''Grouping element to define bit-field properties of a register.'''

    def __init__(self, parent, node):
    #    if not (isinstance(parent, register)):
    #        raise TypeError("Only parent 'register' allowed")
        svd.classes.parent.__init__(self, parent, node)

class field(svd.classes.dim):
    '''All fields of a register are enclosed between the <fields> opening and closing tags.'''

    attributes = ['access']

    def __init__(self, parent, node, name = None, offset = 0):
        svd.classes.dim.__init__(self, parent, node, name, offset)

        attr = {}
    #    attr['name'] = svd.parser.text(svd.node.elememnt(node, 'name', True))
    #    attr['description'] = svd.parser.text(svd.node.element(node, 'description'))

        # bitRangeOffsetWidthStyle
        bit_offset = svd.parser.integer(svd.node.element(node, 'bitOffset'))
        bit_width = svd.parser.integer(svd.node.element(node, 'bitWidth'))
        if bit_offset is not None:
            # If bitWidth is not set, default is 1
            bit_width = 1 if bit_width is None else bit_width
        else:
            # bitRangeLsbMsbStyle
            lsb = svd.parser.integer(svd.node.element(node, 'lsb'))
            msb = svd.parser.integer(svd.node.element(node, 'msb'))
            if lsb is None or msb is None:
                bit_range = svd.parser.text(svd.node.element(node, 'bitRange'))
                if bit_range is None:
                    raise ValueError("Field '{}' has no valid bit-range".format(attr['name']))

                match = re.search('\[([0-9]+):([0-9]+)\]', bit_range)
                lsb = int(match.group(2))
                msb = int(match.group(1))

            bit_offset = lsb
            bit_width = (msb - lsb) + 1

        attr['bit_offset'] = bit_offset
        attr['bit_width'] = bit_width

        attr['access'] = svd.parser.enum(svd.type.access, svd.node.element(node, 'access'))
        attr['modified_write_values'] = svd.parser.enum(svd.type.modified_write_values, svd.node.element(node, 'modifiedWriteValues'))
        attr['read_action'] = svd.parser.enum(svd.type.read_action, svd.node.element(node, 'readAction'))
        self.add_attributes(attr)

    #    self.write_constraint_node = write_constraint.add_elements(self, write_constraint_node)

        write_constraint_node = node.find('./writeConstraint')
        if write_constraint_node is not None:
            self.write_constraint = write_constraint(self, write_constraint_node)

        enumerated_values_node = node.find('./enumerated_values')
        if enumerated_values_node is not None:
            self.enumerated_values = enumerated_values(self, enumerated_values_node)

class enumerated_values(svd.classes.parent):
    '''The concept of enumerated values creates a map between unsigned integers and an identifier string. In addition, a description string can be associated with each entry in the map.'''

    def __init__(self, parent, node):
        svd.classes.parent.__init__(self, parent, node)

        attr = {}
        attr['name'] = svd.parser.text(svd.node.element(node, 'name'))
        attr['header_enum_name'] = svd.parser.text(svd.node.element(node, 'headerEnumName'))
        attr['usage'] = svd.parser.enum(svd.type.enum_usage, svd.node.element(node, 'usage'), svd.type.enum_usage.read_write)
        self.add_attributes(attr)

        self.enumerated_value = []
        for child in node.findall('./enumeratedValue'):
            self.enumerated_value.append(enumerated_value(self, child))

        if len(self.enumerated_value) == 0:
            raise SyntaxError("At least one element of enumeratedValue is needed in enumeratedValues '{}'".format(attr['name']))

class enumerated_value(svd.classes.parent):
    '''An enumeratedValue defines a map between an unsigned integer and a string.'''

    def __init__(self, parent, node):
        svd.classes.parent.__init__(self, parent, node)

        attr = {}
        attr['name'] = svd.parser.text(svd.node.element(node, 'name'))
        attr['description'] = svd.parser.text(svd.node.element(node, 'description'))
        attr['value'] = svd.parser.integer(svd.node.element(node, 'value'))
        attr['is_default'] = svd.parser.boolean(svd.node.element(node, 'isDefault'))
        if attr['value'] is None and attr['is_default'] is None:
            raise SyntaxError("Either 'value' or 'isDefault' is mandatory in enumeratedValue '{}'".format(attr['name']))
        self.add_attributes(attr)