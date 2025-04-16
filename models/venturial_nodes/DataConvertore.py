from pyvnt import *

class DataConvertorNodeToPyVNT:
    """
    Converts Blender node data to PyVNT data structures.
    
    This class provides methods to convert various types of Blender node data
    (integers, floats, strings, vectors, etc.) to their corresponding PyVNT
    data types for use in the PyVNT system.
    """
    def __init__(self):
        """Initialize the converter with an empty data dictionary."""
        self.data = {}

    def convert_To_Int_C(self, name:str, value:int, minimum:int, maximum:int):
        """
        Convert an integer value to a PyVNT Int_P object.
        
        Args:
            name (str): Name of the Int_P object
            value (int): Integer value to store
            minimum (int): Minimum allowed value
            maximum (int): Maximum allowed value
            
        Returns:
            Int_P: A PyVNT integer property object
        """
        return Int_P(name, value,minimum= minimum, maximum= maximum)
    
    def convert_To_Flt_C(self, name:str, value:float, minimum:float, maximum:float):
        """
        Convert a float value to a PyVNT Flt_P object.
        
        Args:
            name (str): Name of the Flt_P object
            value (float): Float value to store
            minimum (float): Minimum allowed value
            maximum (float): Maximum allowed value
            
        Returns:
            Flt_P: A PyVNT float property object
        """
        return Flt_P(name, value,minimum= minimum, maximum= maximum)
    
    def convert_To_Str_C(self, name:str, value:str):
        """
        Convert a string value to a PyVNT Str_P object.
        
        Args:
            name (str): Name of the Str_P object
            value (str): String value to store
            
        Returns:
            Str_P: A PyVNT string property object
        """
        return Str_P(name, value)
    
    def convert_To_Enm_C(self, name:str, value:str):
        """
        Convert a string value to a PyVNT Enm_P (enum) object.
        
        Args:
            name (str): Name of the Enm_P object
            value (str): String value to store as the selected enum option
            
        Returns:
            Enm_P: A PyVNT enum property object with the specified value
        """
        return Enm_P(name, {value},value)
    
    def convert_To_Dim_Set_C(self, name:str, value:list):
        """
        Convert a list of dimension values to a PyVNT Dim_Set_P object.
        
        Args:
            name (str): Name of the Dim_Set_P object
            value (list): List of 7 integer values representing dimensions
                         [mass, length, time, temperature, moles, current, luminosity]
            
        Returns:
            Dim_Set_P: A PyVNT dimension set property object
        """
        return Dim_Set_P(name, value)

    def convert_To_VecTor_List_CP(self, name:str,minimum:float,maximum:float, value:list):
        """
        Convert a vector (x,y,z) to a PyVNT List_CP object containing float properties.
        
        Args:
            name (str): Name of the List_CP object
            minimum (float): Minimum allowed value for all components
            maximum (float): Maximum allowed value for all components
            value (list): List of 3 values [x, y, z] representing vector components
            
        Returns:
            List_CP: A PyVNT list container with three Flt_P objects for x, y, z
        """
        vector_list = List_CP(name, elems=[[
            Flt_P("x", value[0], minimum=minimum, maximum=maximum),
            Flt_P("y", value[1], minimum=minimum, maximum=maximum),
            Flt_P("z", value[2], minimum=minimum, maximum=maximum)
        ]])
        return vector_list
    
    def convert_To_Str_P(self, name:str, value:str):
        """
        Convert a string value to a PyVNT Enm_CP (container enum) object.
        
        Args:
            name (str): Name of the Enm_CP object
            value (str): String value to store
            
        Returns:
            Enm_CP: A PyVNT enum container property
        """
        return Enm_P(name,{value},value)
    
    def convert_To_Dim_Set_C(self, name:str, value:list):
        """
        Convert a list of dimension values to a PyVNT Dim_Set_P object.
        Duplicate method maintained for backward compatibility.
        
        Args:
            name (str): Name of the Dim_Set_P object
            value (list): List of 7 integer values representing dimensions
                         [mass, length, time, temperature, moles, current, luminosity]
            
        Returns:
            Dim_Set_P: A PyVNT dimension set property object
        """
        return Dim_Set_P(name, value)
    
    def convert_To_MultiValue_List_CP(self, name:str, minimum:float, maximum:float, num_values, value_type:str):
        """
        Convert a list of values to a PyVNT MultiValue_List_CP object.
        
        Args:
            name (str): Name of the MultiValue_List_CP object
            minimum (float): Minimum allowed value for all components
            maximum (float): Maximum allowed value for all components
            num_values (int): Number of values in the list
            value_type (str): Type of value to store in the list
            
        Returns:
            MultiValue_List_CP: A PyVNT multi-value list container
        """
        listnode=List_CP(name)
        for i in num_values:
            if value_type == "FLOAT":
                listnode.append_elem([Flt_P(f"Value_{i}",i.default_value,minimum=minimum,maximum=maximum)])
            elif value_type == "INT":
                minimum=int(minimum)
                maximum=int(maximum)
                listnode.append_elem([Int_P(f"Value_{i}",i.default_value,minimum=minimum,maximum=maximum)])
        return listnode

