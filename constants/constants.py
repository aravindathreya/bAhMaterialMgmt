# 22 fields
project_fields = ['project_number', 'project_name','package_type', 'project_location', 'no_of_floors', 'project_value', 'date_of_initial_advance',
            'date_of_agreement', 'sales_executive', 'site_area','basement_slab_area',
            'gf_slab_area', 'ff_slab_area','sf_slab_area','tf_slab_area','fof_slab_area','fif_slab_area', 'tef_slab_area', 'shr_oht','additional_cost' ,'elevation_details',
            'paid_percentage', 'comments', 'is_approved', 'cost_sheet', 'site_inspection_report','created_at','client_name','client_phone','agreement']
roles = [
            'QS Head',
            'QS Info',
            'QS Engineer',
            'Purchase Head',
            'Purchase Executive',
            'Project Coordinator',
            'Project Manager',
            'Design Head',
            'Senior Architect',
            'Architect',
            'Structural Designer',
            'Electrical Designer',
            'PHE Designer',
            'Site Engineer',
            'Sales Executive',
            'Billing',
            'Finance',
            'Planning',
            'Purchase Info',
            'Client'
        ]

# WIP
roleToAccess = {
    'Super Admin': [
        'Create project', 
        'View unapproved projects',
        'View approved projects',
        'View archived projects',
        'Create user',
        'View user',
        'Edit user',
        'Delete user',
        'Vendor registration',
        'View vendors',
        'KYP for material',
        'Enter material',
        'Shifting entry',
        'View inventory',
        'View Indents for QS',
        'View Indents for purchase',
        'View Unapproved  POs',
        'View Approved  POs',
        'Deleted Indents',
        'Contractor registration',
        'View Contractors',
        'Edit Contractors',
        'Delete Contractors',
        'Create work order',
        'View unsigned work orders',
        'View unapproved work orders',
        'View approved work orders',
        'Debit note',
        'Create bill',
        'View unapproved bills',
        'View approved bills',
        'View archived bills',
        'View drawings',
        'View revised drawings',
        'View drawing requests'
        ]
}

materials = [
        'PCC M 7.5',
        'PCC M 15',
        'M 20',
        'M 25',
        'Red Bricks',
        'Exposed Bricks',
        'Wirecut bricks',
        'Earth Blocks',
        'Interlocking Blocks',
        'Solid blocks 4"',
        'Solid blocks 6"',
        'Solid blocks 8"',
        'Porotherm Full blocks 8"',
        'Porotherm Full blocks 6"',
        'Porotherm Full blocks 4"',
        'Porotherm End blocks 8"',
        'Porotherm End blocks 6"',
        'Porotherm End blocks 4"',
        'AAC Blocks 8"',
        'AAC Blocks 6"',
        'AAC Blocks 4"',
        'Glass blocks',
        'Jaali blocks',
        'Door frames',
        'Door Beading',
        'Door Shutters',
        'Windows frames',
        'Windows shutters',
        'UPVC windows',
        'Aluminum windows',
        'Window glass',
        'Hexagonl Rod',
        'Granite',
        'Tiles',
        'Marble',
        'Kota stone',
        'HPL Cladding',
        'Shera Cladding',
        'Floor mat',
        'Plumbing',
        'Sanitary',
        'Aggregates 12mm',
        'Aggregates 20mm',
        'Aggregates 40mm',
        'Cinder',
        'Size stone',
        'Boulders',
        'River sand',
        'POP',
        'white cement',
        'tile adhesive',
        'tile grout',
        'lime paste',
        'Sponge',
        'chicken mesh',
        'Motor',
        'Curing Pipe',
        'Helmet',
        'Jackets',
        'GI sheets',
        'Tarpaulin',
        'Nails',
        'Cement',
        'Steel',
        'M Sand',
        'P Sand',
        'Teak wood frame',
        'Sal wood frame',
        'Honne wood frame',
        'Teak wood door',
        'Sal wood door',
        'Flush door' ,
        'Binding wire',
        'Hardwares' ,
        'Chamber Covers' ,
        'Filler slab material',
        'Electrical',
        'Water tank',
        'Plywwod',
        'Laminates',
        'Blocks Adhesive',
        'GI sheets',
        'Mahogany frames',
        'WPC Frames',
        'WPC Doors',
        'Stone cladding',
        'Brick cladding',
        'Plain glass',
        'Toughned glass',
        'Polycorbonate sheet',
        'Laterite stone',
        'Name board',
        'M30'
    ]        