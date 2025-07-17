# Flowsheet Processor API

Python interface to a flowsheet that makes it easier to use by humans and provides the required interface for the Flowsheet Processor UI.

{octicon}`mark-github` [GitHub repository](https://github.com/prommis/idaes-flowsheet-processor)
<!-- 
{octicon}`book` [Documentation](https://idaes-ui.readthedocs.io/en/latest/user/fv/)
-->

## Major features

* Export input and output variables, with human-readable names and units
* Define standard actions such as 'build' and 'report' to simplify interactive usage

## Compatibility

The Python API will work in all operating systems, and is usable with any IDAES flowsheet.

## Screenshots

The most common use of the Flowsheet Processor API is to "wrap" a flowsheet for use in the Flowsheet Processor.
This is done by defining a Python module alongside the code that implements the flowsheet, 
typically ending in "_ui.py", that defines the special method `export_to_ui`.

:::{note}
The function `export_to_ui()` will be renamed to the more general `flowsheet_interface()`
in future releases. Both names will work for the foreseeable future.
:::

```python
from idaes_flowsheet_processor.api import FlowsheetInterface
# ..also need to import model components, etc. that define the flowsheet

##########################################################
# This function name is special; if present, it it used
# to create the flowsheet wrapper, which is an instance
# of the FlowsheetInterface class.
#########################################################
def export_to_ui():
    return FlowsheetInterface(
        name="RO with energy recovery",
        do_export=export_variables,
        do_build=build_flowsheet,
        do_solve=solve_flowsheet,
    )

# Selected sections of a variable export call
def export_variables(flowsheet=None, exports=None, build_options=None, **kwargs):
    fs = flowsheet
    # --- Input data ---
    # Feed conditions
    exports.add(
        obj=fs.feed.properties[0].flow_mass_phase_comp["Liq", "H2O"],
        name="Water mass flowrate",
        ui_units=pyunits.kg / pyunits.s,
        display_units="kg/s",
        rounding=3,
        description="Inlet water mass flowrate",
        is_input=True,
        input_category="Feed",
        is_output=False,
    )
    exports.add(
        obj=fs.feed.properties[0].flow_mass_phase_comp["Liq", "NaCl"],
        name="NaCl mass flowrate",
        ui_units=pyunits.kg / pyunits.s,
        display_units="kg/s",
        rounding=3,
        description="Inlet NaCl mass flowrate",
        is_input=True,
        input_category="Feed",
        is_output=False,
    )

    # Unit model data, feed pump
    exports.add(
        obj=fs.P1.efficiency_pump[0],
        name="Pump efficiency",
        ui_units=pyunits.dimensionless,
        display_units="fraction",
        rounding=2,
        description="Efficiency of feed pump",
        is_input=True,
        input_category="Feed Pump",
        is_output=False,
    )

    # .... etc ...

    # Product
    exports.add(
        obj=fs.product.properties[0].flow_vol,
        name="Volumetric flow rate",
        ui_units=pyunits.m**3 / pyunits.hr,
        display_units="m3/h",
        rounding=2,
        description="Outlet product water volumetric flow rate",
        is_input=False,
        is_output=True,
        output_category="Product",
    )
    exports.add(
        obj=fs.product.properties[0].conc_mass_phase_comp["Liq", "NaCl"],
        name="NaCl concentration",
        ui_units=pyunits.g / pyunits.L,
        display_units="g/L",
        rounding=3,
        description="Outlet product water NaCl concentration",
        is_input=False,
        is_output=True,
        output_category="Product",
    )

    def build_flowsheet(erd_type=ERDtype.pump_as_turbine, build_options=None, **kwargs):
         # build and solve initial flowsheet
         # ...

         return m # the flowsheet

    def solve_flowsheet(flowsheet=None):
        # solve the flowsheet
        # ...

        return results

```