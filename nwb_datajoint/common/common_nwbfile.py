import os
import datajoint as dj

schema = dj.schema("common_lab", locals())

import kachery as ka

# TODO: make decision about docstring -- probably use :param ...:

@schema
class Nwbfile(dj.Manual):
    definition = """
    nwb_file_name: varchar(400)
    ---
    nwb_file_sha1: varchar(40)
    """
    def insert_from_relative_file_name(self, nwb_file_name):
        """Insert a new session from an existing nwb file.

        Args:
            nwb_file_name (str): Relative path to the nwb file
        """
        nwb_file_abspath = Nwbfile.get_abs_path(nwb_file_name)
        assert os.path.exists(nwb_file_abspath), f'File does not exist: {nwb_file_abspath}'

        print('Computing SHA-1 and storing in kachery...')
        with ka.config(use_hard_links=True):
            kachery_path = ka.store_file(nwb_file_abspath)
            sha1 = ka.get_file_hash(kachery_path)
        
        self.insert1(dict(
            nwb_file_name=nwb_file_name,
            nwb_file_sha1=sha1
        ), skip_duplicates=True)
    
    @staticmethod
    def get_abs_path(nwb_file_name):
        base_dir = os.getenv('NWB_DATAJOINT_BASE_DIR', None)
        assert base_dir is not None, 'You must set NWB_DATAJOINT_BASE_DIR or provide the base_dir argument'

        nwb_file_abspath = os.path.join(base_dir, nwb_file_name)
        return nwb_file_abspath

