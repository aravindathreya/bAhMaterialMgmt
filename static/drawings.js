drawings_list = []
var actionBtn;
var action;
var project_id;
var drawing_name;
var drawing_link;
var drawingsTableNameMap = {
    'Working Drawings': 'wokring_drawing',
    'Misc Details': 'misc_details',
    'Filter slab layout': 'filler_slab_layout',
    'Sections': 'sections',
    '2d elevation': '2d_elevation',
    'Door window details, Window grill details': 'door_window_details_window_grill_details',
    'Flooring layout details': 'flooring_layout_details',
    'Toilet kitchen dadoing details': 'toilet_kitchen_dadoing_details',
    'Compound wall details': 'compound_wall_details',
    'Fabrication details':'fabrication_details',
    'Sky light details': 'sky_light_details',
    'External and internal paint shades': 'external_and_internal_paint_shades',
    'Isometric views': 'isometric_views',
    '3d drawings': '3d_drawings',
    'Column marking': 'column_marking',
    'Footing layout': 'footing_layout',
    'UG sump details': 'ug_sump_details',
    'Plinth beam layout': 'plinth_beam_layout',
    'Staircase details': 'staircase_details',
    'Floor form work beam and slab reinforcement details': 'floor_form_work_beam_and_slab_reinforcement_details',
    'OHT slab details': 'oht_slab_details',
    'Lintel details': 'lintel_details',
    'Electrical drawing': 'electrical_drawing', 
    'Conduit drawing': 'conduit_drawing',
    'Water line drawing': 'water_line_drawing', 
    'Drinage line drawing': 'drainage_line_drawings',
    'RWH details': 'rwh_details'
}

$('th').each(function (index, element) {
    if (index != 0)
        drawings_list.push(element.innerHTML)
})

$('.upload-drawing-for-request').on('click', function() {
    $('.drawing-links').html('')

    project_name = $($(this).parents('tr').find('td').get(0)).text()
    project_id = $($(this).parents('tr').find('td').get(0)).attr('data-project-id')
    request_id = $($(this).parents('tr').find('td').get(0)).attr('data-request-id')

    $('#drawing_request_id').val(request_id)
    $('#project_id').val(project_id)
    $('.project_name').text(project_name)

    drawing_name =  $($(this).parents('tr').find('td').get(3)).text()
    $('#drawing_name').val(drawingsTableNameMap[drawing_name])
    $('.drawing_name').text(drawing_name)

    category =  $($(this).parents('tr').find('td').get(2)).text().trim()
    if(category == 'Artchitectural') {
        category = 'architect_drawings'
    } else if(category == 'Structural') {
        category = 'structural_drawings'
    } else if(category == 'Electrical') {
        category = 'electrical_drawings'
    } else if(category == 'Plumbing') {
        category = 'plumbing_drawings'
    }
    $('#category').val(category)

    action = 'Complete'
    $('.current-status').text('Changing status to ' + action)
})

$('.status-action').on('click', function () {
    $('.current-status').text('')
    actionBtn = $(this).find('div')
    $('.upload-drawing-form').addClass('d-none')
    $('.drawing-links').html('')
    $('.drawing-complete').text('Complete')

    drawing_link = $(this).attr('data-link').toString()

    if (drawing_link == 'None' || drawing_link == '0' || drawing_link == '-1' || drawing_link == '') {
        $('.drawing-link-section').addClass('d-none')
    }
    else {
        $('.drawing-link-section').removeClass('d-none')
        drawings = $(this).attr('data-link').toString().split('||')
        index = 1;
        for (const drawing of drawings) {
            let drawingLink = document.createElement("A")
            $(drawingLink).text('View drawing '+index.toString())
            $(drawingLink).addClass('drawing-link')
            $(drawingLink).attr('href', '/files/' + drawing)
            $(drawingLink).attr('target', '_blank')
            $('.drawing-links').append(drawingLink)
            index++;
            $('.drawing-complete').text('Revise')
        }        
    }

    project_name = $($(this).parents('tr').find('td').get(0)).text()
    project_id = $($(this).parents('tr').find('td').get(0)).attr('data-project-id')

    $('#project_id').val(project_id)
    $('.project_name').text(project_name)

    index = $(this).attr('data-index')
    drawing_name = drawings_list[index]
    $('.drawing_name').text(drawing_name)
    $('#drawing_name').val(drawing_name)
})

$('.drawing-complete').on('click', function () {
    action = 'Complete';
    $('.current-status').text('Changing status to ' + action)
    $('.upload-drawing-form').removeClass('d-none')
})

$('.drawing-in-progress').on('click', function () {
    action = 'In progress';
    $('.current-status').text('Changing status to ' + action)
    $('.upload-drawing-form').addClass('d-none')
})

$('.drawing-pending').on('click', function () {
    action = 'Pending';
    $('.current-status').text('Changing status to ' + action)
    $('.upload-drawing-form').addClass('d-none')
})

$('.drawing-not-applicable').on('click', function () {
    action = 'Not applicable';
    $('.current-status').text('Changing status to ' + action)
    $('.upload-drawing-form').addClass('d-none')
})


$('.approve_drawing_btn').on('click', function () {

    if (action == "Complete") {
        if (actionBtn) {
            actionBtn.find('.status').addClass('d-none')
            actionBtn.find('.bg-success').removeClass('d-none')            
        }
        if ($('#drawing').val().length) {
            $('.upload-drawing-form').submit()
        } else {
            alert('You must upload the drawing to mark it as complete')
        }
    } else if (action == "In progress") {
        actionBtn.find('.status').addClass('d-none')
        actionBtn.find('.bg-warning').removeClass('d-none')

        if ($('.drawing-link').length) {
            if (confirm('Are you sure you want to change the status of this to in progress. Older drawings will be removed')) {
                $.ajax({
                    type: "POST",
                    url: "/mark_drawing_in_progress",
                    success: function (data) {
                        window.location.href = '/drawings'
                    },
                    error: function (error) {
                        console.log(error)
                        // handle error
                    },
                    async: true,
                    data: { 'project_id': project_id, 'drawing_name': drawing_name },
                });
            }
        }

       
    } else if (action == "Pending") {
        actionBtn.find('.status').addClass('d-none')
        actionBtn.find('.bg-danger').removeClass('d-none')

        if ($('.drawing-link').length) {
            if (confirm('Are you sure you want to change the status of this to pending. Older drawings will be removed')) {
                $.ajax({
                    type: "POST",
                    url: "/change_drawing_status",
                    success: function (data) {
                        window.location.href = '/drawings'
                    },
                    error: function (error) {
                        console.log(error)
                        // handle error
                    },
                    async: true,
                    data: { 'project_id': project_id, 'drawing_name': drawing_name,'action': 'pending' },
                });
            }
        } else {
            $.ajax({
                type: "POST",
                url: "/change_drawing_status",
                success: function (data) {
                    window.location.href = '/drawings'
                },
                error: function (error) {
                    console.log(error)
                    // handle error
                },
                async: true,
                data: { 'project_id': project_id, 'drawing_name': drawing_name,'action': 'pending' },
            });
        }

        
    } else if (action == "Not applicable") {
        actionBtn.find('.status').addClass('d-none')
        actionBtn.find('.bg-primarys').removeClass('d-none')

        if ($('.drawing-link').length) {
            if (confirm('Are you sure you want to change the status of this to not applicable. Older drawings will be removed')) {
                $.ajax({
                    type: "POST",
                    url: "/change_drawing_status",
                    success: function (data) {
                        window.location.href = '/drawings'
                    },
                    error: function (error) {
                        console.log(error)
                        // handle error
                    },
                    async: true,
                    data: { 'project_id': project_id, 'drawing_name': drawing_name,'action': 'not_applicable' },
                });
            }
        } else {
            $.ajax({
                type: "POST",
                url: "/change_drawing_status",
                success: function (data) {
                    window.location.href = '/drawings'
                },
                error: function (error) {
                    console.log(error)
                    // handle error
                },
                async: true,
                data: { 'project_id': project_id, 'drawing_name': drawing_name,'action': 'not_applicable' },
            });
        }
        
        
    }
})