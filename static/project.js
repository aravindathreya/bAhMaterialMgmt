// In your Javascript (external .js resource or <script> tag)
$(document).ready(function () {   

    $("#generate_material_report").on('click', function(){
        if($(this).text().trim() == 'Generating') return;
        $(this).text('Generating')
        $.ajax({
            url: '/material_report',
            type: "GET",
        
            success: function (data) {
                $("#generate_material_report").addClass('d-none')
            },
        });
    })

    $("#generate_trade_report").on('click', function(){
        if($(this).text().trim() == 'Generating') return;
        $(this).text('Generating')
        $.ajax({
            url: '/trade_report',
            type: "GET",
        
            success: function (data) {
                $("#generate_trade_report").addClass('d-none')
            },
        });
    })

    $('#get_expenses').on('click', function(){
        const project = $("#project").val()
        if(project.length) {
            window.location.href = '/expenses?project_id='+project.toString()       
        }
    })

    $(".metric_name").each(function(index, element) {
        const metric_name = $(element).text().replaceAll('_',' ') 
        $(element).text(metric_name)
    })

    $(".spin_up").each(function(index, element) {
        const value = $(element).attr('data-value')
        if (parseInt(value) == 0) $(element).text(value.toString()) 
        else {
            var initValue = parseInt(value) > 100 ? parseInt(value) - 50 : parseInt(value) - 10
            const interval = setInterval(() => {
                if (initValue >= parseInt(value)) clearInterval(interval)
                $(element).text(initValue.toString())
                initValue += 1;
                
            }, 10)
        }
        
    })
    

    $('.edit-task').on('click', function () {
        $("#EditTaskModal .task_id").val($(this).parents('.task-card').find('.task_id').text().trim())
        $("#EditTaskModal .task-name").val($(this).parents('.task-card').find('.task-name').text().trim())
        $("#EditTaskModal .task-start-date").val($(this).parents('.task-card').find('.task-start-date').text().trim())
        $("#EditTaskModal .task-end-date").val($(this).parents('.task-card').find('.task-end-date').text().trim())
        $("#EditTaskModal .task-percent").val($(this).parents('.task-card').find('.task-percent').text().trim())
    })

    function initSearchProject() {
        console.log('initSearchProject')
        $('.search-project-field').on('keyup', function() {
            let searchValue = $('.search-project-field').val();
            if(searchValue.trim().length == 0) $('.project-card').parent().removeClass('d-none')
            else {
                $('.project-card').parent().addClass('d-none')
                $('.project-card').each(function(index, element) {
                    if($(element).find('.project-name').text().toLowerCase().trim().includes(searchValue.toLowerCase().trim())) {               
                        $(element).parent().removeClass('d-none')
                    }
                })
            }
        })

        $('.search-po-field').on('keyup', function() {
            let searchValue = $('.search-po-field').val();
            if(searchValue.trim().length == 0) $('.project-name').removeClass('d-none')
            else {
                $('.collapse.show').collapse('hide');
                $('.project-name').addClass('d-none')
                $('.project-name').each(function(index, element) {
                    if($(element).text().toLowerCase().trim().includes(searchValue.toLowerCase().trim())) {               
                        $(element).removeClass('d-none')                        
                    }
                })
            }
        })
    }

    initSearchProject()

    if($(".percentage-for-stage").length > 1) {
        total_perc = 0
        $(".percentage-for-stage").each(function(index, element){
            if($(element).parents('tr').find('.billed_amount').text().trim() != '0' && $(element).text().trim() != '') total_perc += parseFloat($(element).text())
        })
        $(".percentage-column-header").text(`${total_perc}%`)
    }

    $('.delete_bill').on('click',function(){
        if (confirm('Are you sure you want to delete this bill')) {
            let btn = $(this) 
            let delete_url = $(this).attr('data-delete-url');
            $.ajax({
                url: delete_url,
                type: "GET",
            
                success: function (data) {
                    console.log(data)
                    btn.parents('tr').remove();
                },
            });
        }
    })

    if($('.contractor-profile-picture').length) {
        $('.contractor-profile-picture').each(function(index, element){
            const src = $(element).attr('data-src')
            $(element).attr('src', src)
        })
    }

    $('.block-project').on('click', function() {
        project_id = $(this).attr('data-project-id')
        $('.project_id').val(project_id)
    })


    if($('.edit-procurement-material').length) {
        $('#material').val($('.edit-procurement-material').text())
        $('#material').trigger('change')

        $('#unit').val($('.edit-procurement-unit').text())
        $('#unit').trigger('change')

        $('#gst').val($('.edit-procurement-gst').text())
        $('#gst').trigger('change')
        
    }

    $('.approve-indent-by-ph').on('click', function(e) {
        e.preventDefault()
        url = $(this).attr('href')
        difference_cost = $(".final_difference_cost").val().toString()
        if (difference_cost.trim() != '') {
            url += '&difference_cost='+difference_cost
            window.location.href = url;
        }

    })

    setTimeout(() => {
        if ($('.kyp_material_page').length > 0) {
            $('input').on('keydown', function(e) {
                if (e.keyCode === 190 || e.keyCode === 110) {
                e.preventDefault();
                }
            })
        }

        if ($('.edit_vendor_material_type').length > 0) {
            $('#edit_vendor_material_type_select').val($('.edit_vendor_material_type').text())
            $('#edit_vendor_material_type_select').trigger('change')

            let materials = $('.edit_vendor_material_type').text()
            materials = materials.replaceAll("'","")
            materials = materials.split(',')
            stripped_materials = []
            for(const material of materials) 
                stripped_materials.push(material.trim())
            console.log(stripped_materials)
            $("#edit_vendor_material_type_select").val(stripped_materials)
            $("#edit_vendor_material_type_select").trigger('change')
        }

        if ($('#indent_material').length > 0) {
            $('#material').val($('#indent_material').text())
            $('#material').trigger('change')
        }

        if ($('#indent_unit').length > 0) {
            $('#unit').val($('#indent_unit').text())
            $('#unit').trigger('change')
        }

        if($('.vendor-location').length > 0) {
            let vendor_locations = $('.vendor-location').text()
            vendor_locations =vendor_locations.replaceAll("'","")
            vendor_locations = vendor_locations.split(',')
            stripped_vendor_locations = []
            for(const location of vendor_locations) 
                stripped_vendor_locations.push(location.trim())
            $("#location").val(stripped_vendor_locations)
            $("#location").trigger('change')
        }

        // $('.select2.select2-container').on('click', function(){
        //     setTimeout(() => {
        //         $(this).parents().find('.select2-search__field').get(0).focus()
        //     }, 500)
        // })
    }, 1000)

    if($('.approved_amount').length && $('.total_paid').length) {
        total_paid = 0;
        $('.approved_amount').each(function(index, element) {
            if ($(element).text().toString().length) {
                total_paid += parseInt($(element).text())
            }
        })
        total_billed = 0;
        $('.billed_amount').each(function(index, element) {
            if ($(element).text().toString().length && !$(element).parent('tr').find('.stage').text().trim().includes('Clearing balance')) {
                total_billed += parseInt($(element).text())
            }
        })

        total_billed_but_not_approved = 0;
        unapproved_bill_exists = false;
        $('.billed_amount').each(function(index, element) {
            if($(element).text().toString().trim() != '0' && $(element).parent('tr').find('.approved_amount').text().trim().toString() == '0') {
                unapproved_bill_exists = true;
            }
            if ($(element).text().toString().length && $(element).parent('tr').find('.approved_amount').text().trim().toString() != '0') {
                total_billed_but_not_approved += parseInt($(element).text())
            }
        })
        $('.balance').text(total_billed -  total_paid)
        $('.total_billed').text(total_billed)
        $('.total_paid').text(total_paid)

        if(total_billed_but_not_approved - total_paid > 0 && !unapproved_bill_exists) {
            balance_amnt = total_billed_but_not_approved - total_paid;
            contractor_name = $('.contractor_name').text()
            contractor_code = $('.contractor_code').text()
            contractor_pan = $('.contractor_pan').text()
            project_id = $('.project_id').text()
            trade =  $('.trade').text()
            work_order_id = $('.work_order_id').text()
            $.ajax({
                url: '/check_if_clear_balance_bill_due',
                type: "POST",
                dataType: 'json',
                data: {
                 'balance_amnt': balance_amnt,
                 'contractor_name': contractor_name,
                 'contractor_code': contractor_code,
                 'contractor_pan': contractor_pan,
                 'project_id': project_id,
                 'trade': trade,
                 'work_order_id': work_order_id,

                },
                success: function (data) {
                    // if(data['message'] === 'Bill for clearing balance does not exists') $('.clear-balance-btn').removeClass('d-none')
                    // else $('.clear-balance-bill-raised').removeClass('d-none')
                },
            });
            
        }
    }

    window.onload = function(){
        console.log(window.location.href.includes('exported=true'))
        setTimeout(() => {
            if(window.location.href.includes('exported=true')) {
                window.location.href = '/static/bills.xls'
            }
        }, 2000)
    }

    if(window.location.href.includes('view_indent_details')) { 
        let indentStatus = $(".indent-status").text().trim()
        if(indentStatus == 'approved') $('.view_qs_approval_indents_nav_btn').addClass('active')
        if(indentStatus == 'approved_by_qs') $('.view_approved_indents_nav_btn').addClass('active')
        if(indentStatus == 'po_uploaded') $('.view_approved_POs_nav_btn').addClass('active')
        if(indentStatus == 'approved_by_ph') $('.view_ph_approved_indents_nav_btn').addClass('active')

    }

    $('.nav-link').on('click', function() {
        localStorage.setItem('sidebarScrollTop', $('.sidebar').scrollTop())
    })

    // if ( $('.nav-link.active').length ) $('.nav-link.active').get(0).scrollIntoView({
    //         behavior: "smooth"
    //     })
    if ( $('.nav-link.active').length ) {
        const sidebarScrollTop = localStorage.getItem('sidebarScrollTop')
        if(sidebarScrollTop) {
            console.log(sidebarScrollTop)
            $('.sidebar').scrollTop(sidebarScrollTop)
        }
    }

    $(document).mouseup(function (e) {
        var container = $(".sidebar");
        var menu_icon = $('.mobile-menu-icon');
        // if the target of the click isn't the container nor a descendant of the container
        if (!container.is(e.target) && container.has(e.target).length === 0 &&
            !menu_icon.is(e.target) && menu_icon.has(e.target).length === 0
        ) {
            container.removeClass('active');
        }
    });

    $('#get_notes').on('click', function(){
        const project = $("#project").val()
        if(project.length)
            window.location.href = '/project_notes?project_id='+project.toString()
    })

    $('.mobile-menu-icon').on('click', function () {
        $('.sidebar').hasClass('active') ? $('.sidebar').removeClass('active') : $('.sidebar').addClass('active')
    })

    $('.select2').select2();

    $(function () {
        $('[data-toggle="popover"]').popover({
            trigger: 'focus'
        })
    })

    $(function () {
        $('[data-toggle="popover-hover"]').popover({
            trigger: 'hover'
        })
    })

    $(".material-select").on('change', function() {
        $(".vendor-select").empty()
        $(".vendor-select").append($("<option></option>"))
        const material_selected = $(this).val().trim()
        $.ajax({
                url: '/get_vendors_for_material',
                type: "POST",
                dataType: 'json',
                data: { 'material_selected': material_selected },
                success: function (data) {
                    for (const vendor of data) {
                        $(".vendor-select").append($("<option></option>")
                            .attr("value", vendor[0])
                            .text(vendor[1]))
                    }
                }
            });
    })

    $(".update_trades_for_project").on('change', function () {
        const project_id = $(this).val()

        $('select_trade_for_bill select').addClass('d-none')
        $('.select_payment_stage').addClass('d-none')
        $(".final_details").addClass('d-none')
        $('#create_bill_form').addClass('d-none')

        if (project_id) {
            $('.select_trade_for_bill').removeClass('d-none')
            $(".select_trade_for_bill select").empty()
            $(".select_trade_for_bill select").append($("<option></option>"))
            $.ajax({
                url: '/update_trades_for_project',
                type: "POST",
                dataType: 'json',
                data: { 'project_id': project_id },
                success: function (data) {        
                    $(".select_trade_for_bill select").append($("<option></option>")
                            .attr("value", 'NT/NMR')
                            .text('NT/NMR'))            
                    for (const trade of data) {
                        $(".select_trade_for_bill select").append($("<option></option>")
                            .attr("value", trade[0])
                            .text(trade[1]))
                    }
                }
            });
        } else {
            $('.select_trade_for_bill').addClass('d-none')
        }
        $(".select_trade_for_bill select").select2()
    })

    if ($('.nt-nmr-section').length > 0) {
        $('#quantity').on('keyup', function(){
            quantity = parseFloat($('#quantity').val())
            rate = parseFloat($('#rate').val()) 
            bill_amount = (quantity * rate) 
            $('.nt_nmr_bill_amount').text(bill_amount.toString())
            $('input[name="nt_nmr_bill_amount"]').val(bill_amount.toString())
        })
        $('#rate').on('keyup', function(){
            quantity = parseFloat($('#quantity').val())
            rate = parseFloat($('#rate').val()) 
            bill_amount = (quantity * rate)
            $('.nt_nmr_bill_amount').text(bill_amount.toString())
            $('input[name="nt_nmr_bill_amount"]').val(bill_amount.toString())
        })
    }

    $(".select_trade_for_bill select").on('change', function () {
        const work_order_id_for_trade = $(this).val()
        console.log(work_order_id_for_trade)
        
        if (work_order_id_for_trade == 'NT/NMR') {
            $('.nt-nmr-section').removeClass('d-none')
            $("#contractor").select2()
            $('.select_payment_stage').addClass('d-none')
            return;
        } else {
            $('.nt-nmr-section').addClass('d-none')
        }


        if (work_order_id_for_trade) {
            $(".select_payment_stage select").empty()
            $('.select_payment_stage').removeClass('d-none')

            $(".select_payment_stage select").append($("<option></option>"))
            project_id = $("#project").val()
            trade = $('#trade').text()
            $.ajax({
                url: '/update_payment_stages',
                type: "POST",
                dataType: 'json',
                data: { 'project_id': project_id, 'work_order_id_for_trade': work_order_id_for_trade, 'trade': trade },
                success: function (data) {
                    console.log(data)
                    $('.total_wo_value').text(data['work_order_value'].replaceAll(',',''))
                    $('.contractor_name').text(data['contractor_name'])
                    $('.contractor_code').text(data['contractor_code'])
                    $('.contractor_pan').text(data['contractor_pan'])
                    for (const stage of Object.keys(data['stages'])) {
                        $(".select_payment_stage select").append($("<option></option>")
                            .attr("value", data['stages'][stage])
                            .text(stage))
                    }
                }
            });
        } else {
            $('.select_payment_stage').addClass('d-none')
        }
        $(".select_payment_stage select").select2()
    })

    $(".select_payment_stage select").on('change', function () {
        let payment_percentage = $(this).val()
        if (payment_percentage) {

            $(".final_details").removeClass('d-none')
            $('#create_bill_form').removeClass('d-none')

            $(".payment_percentage").text(payment_percentage.toString() + "%")
            let work_order_value = parseFloat($('.total_wo_value').text())
            payment_percentage = parseFloat(payment_percentage)
            const bill_amount_before_5_percent_deduction = (work_order_value * (payment_percentage / 100))
            const final_bill_amount = bill_amount_before_5_percent_deduction - (bill_amount_before_5_percent_deduction * 0.05)
            $(".bill_amount").text(final_bill_amount.toString())
        } else {
            $(".final_details").addClass('d-none')
        }
    })

    $(".create_bill").on('click', function () {
        const project_id = $("#project").val()
        $('input[name="project_id"]').val(project_id)

        const trade = $( "#trade option:selected" ).text()
        $('input[name="trade"]').val(trade)

        const stage = $(".select_payment_stage select").find('option:selected').text()
        $('input[name="stage"]').val(stage)

        const payment_percentage = $(".select_payment_stage select").find('option:selected').val()
        $('input[name="payment_percentage"]').val(payment_percentage)

        const amount = $('.bill_amount').text()
        $('input[name="amount"]').val(amount)

        const contractor_name = $('.contractor_name').text()
        $('input[name="contractor_name"]').val(contractor_name)

        const contractor_code = $('.contractor_code').text()
        $('input[name="contractor_code"]').val(contractor_code)

        const contractor_pan = $('.contractor_pan').text()
        $('input[name="contractor_pan"]').val(contractor_pan)

        const quantity = $('#quantity').val()
        $('input[name="quantity"]').val(quantity)

        const rate = $('#rate').val()
        $('input[name="rate"]').val(rate)

        const description = $('#description').val()
        $('input[name="description"]').val(description)

        const contractor = $('#contractor').val()
        $('input[name="contractor"]').val(contractor)

        const nt_nmr_bill_amount = $('.nt_nmr_bill_amount').text()
        $('input[name="nt_nmr_bill_amount"]').val(nt_nmr_bill_amount)
        if ( trade!='NT/NMR' && $('#create_bill_form').hasClass('d-none')) return;
        
        $("#create_bill_form").submit()
    })

    $('.indent-upload-submit').on('click', function(e){
        e.preventDefault()
        const diff_cost = $('.difference_cost').val()
        $('.difference_cost_field').val(diff_cost)

        const po_number = $('.po_number').val()
        $('.po_number_field').val(po_number)

        $('.indent-upload-submit').parents('form').submit()
    })

    function updateApprovalModalDetails(clickedBtn) {
        console.log(clickedBtn)
        if ($(clickedBtn).hasClass('approval_1_btn'))
            $('.approval_level').val('Level 1')
        if ($(clickedBtn).hasClass('approval_2_btn'))
            $('.approval_level').val('Level 2')

        const project_id = $(clickedBtn).attr('data-project-id')
        const project_name = $(clickedBtn).attr('data-project-name')
        const bill_id = $(clickedBtn).attr('data-bill-id')
        const contractor_name = $(clickedBtn).parents('tr').find('.contractor_name').text()
        const contractor_code = $(clickedBtn).parents('tr').find('.contractor_code').text()
        const contractor_pan = $(clickedBtn).parents('tr').find('.contractor_pan').text()
        const trade = $(clickedBtn).parents('tr').find('.trade').text()
        const payment_stage = $(clickedBtn).parents('tr').find('.stage').text()
        const amount = $(clickedBtn).parents('tr').find('.amount').text()
        const total_payable = $(clickedBtn).parents('tr').find('.total_payable').text()

        $('#approvalModal .project_name').text(project_name)
        $('#approvalModal .contractor_name').text(contractor_name)
        $('#approvalModal .contractor_code').text(contractor_code)
        $('#approvalModal .contractor_pan').text(contractor_pan)
        $('#approvalModal .trade').text(trade)
        $('#approvalModal .payment_stage').text(payment_stage)
        $('#approvalModal .amount').text(amount)
        $('#approvalModal .total_payable').text(total_payable)
        $('#approvalModal .bill_id').val(bill_id)
        $('#approvalModal .project_id').val(project_id)
    }

    $(".approval_1_btn").on('click', function () {
        const clickedBtn = this
        updateApprovalModalDetails(this)
    })

    $(".approval_2_btn").on('click', function () {
        const clickedBtn = this
        updateApprovalModalDetails(this)
    })

    $(".copy_from_approval_1_btn").on("click", function () {
        updateApprovalModalDetails(this)
        $('.approval_level').val('Level 2')
        const amount_approved = parseFloat($(this).parents("tr").find(".approval_1").text().trim())
        $("#amount_approved").val(amount_approved)
        $('[data-toggle="popover-hover"]').popover('hide')
        saveApprovedBill()
    })

    function populateApprovalAmountInTable(bill_id, amount_approved, approval_level) {
        let tdTagClass = ''
        if (approval_level === 'Level 1')
            tdTagClass = 'approval_1'
        if (approval_level === 'Level 2')
            tdTagClass = 'approval_2'
        $('.bill-' + bill_id.toString()).find('.' + tdTagClass).text(amount_approved)

    }

    function saveApprovedBill() {
        const bill_id = $('#approvalModal .bill_id').val()
        const approved_amount = $("#amount_approved").val()
        const notes = $("#notes").val()
        const approval_level = $('.approval_level').val()
        const project_id = $("#project_id").val()
        const trade = $('#approvalModal .trade').text()
        const amount = parseFloat($('#approvalModal .total_payable').text())
        const difference_amount = parseFloat(amount) - parseFloat(approved_amount)

        $.ajax({
            url: '/save_approved_bill',
            type: "POST",
            dataType: 'json',
            data: {
                'bill_id': bill_id,
                'approved_amount': approved_amount,
                'notes': notes,
                'approval_level': approval_level,
                'project_id': project_id,
                'trade': trade,
                'difference_amount': difference_amount
            },
            success: function (data) {
                $('#approvalModal').modal('hide');
                $('#amount_approved').val('')
                $("#notes").val('')
                $(".approve_bill_btn").text('Approve')
                populateApprovalAmountInTable(bill_id, approved_amount, approval_level)
            }
        });
    }

    function validateApprovedBillAmnt() {
        const amount = parseFloat($('#approvalModal .total_payable').text())
        const approved_amount = parseFloat($("#amount_approved").val())
        if (approved_amount > 0 && approved_amount <= amount) {
            $('#amount_approved').parent().find('.invalid-message').addClass('d-none')
            return true
        } else {
            $('#amount_approved').parent().find('.invalid-message').text('Amount entered is not valid')
            $('#amount_approved').parent().find('.invalid-message').removeClass('d-none')
        }
        return false;

    }

    $(".approve_bill_btn").on('click', function () {
        if (validateApprovedBillAmnt()) {
            $(".approve_bill_btn").text('...')
            saveApprovedBill()
        }
    })

    function getWorkOrderForSelectedProject() {
        const project = $("#project").val()
        if (project.length) {
            window.location.href = '/view_work_order?project_id=' + project.toString()
        }
    }

    $("#view_work_order").on('click', getWorkOrderForSelectedProject)

    function getRevisedDrawingsForSelectedProject() {
        const project = $("#project").val()
        if (project.length) {
            window.location.href = '/revised_drawings?project_id=' + project.toString()
        }
    }

    $("#view_revised_drawings").on('click', getRevisedDrawingsForSelectedProject)



    function updateSlabArea(project_id) {
        $.ajax({
            url: '/update_slab_area',
            type: "POST",
            dataType: 'json',
            data: {
                'project_id': project_id,
            },
            success: function (data) {
                console.log(data)
                $('.total_bua_summation').text(data)
            }
        });
    }

    $(".work_order_project_select").on('change', function () {
        const project_id = $(this).val()
        if (project_id) updateSlabArea(project_id)
    })

    $('.add-elevation-detail').on('click', function () {
        element = $($(this).parent().find('.elevation-details').get(0))
        if (element.hasClass('d-none')) {
            element.removeClass('d-none')
        } else {
            clone = element.clone()
            clone.val('')
            element.parent().append(clone)
        }
        return false
    })

    $('.add-additional-cost').on('click', function () {
        element = $($(this).parent().find('.additional-cost').get(0))
        if (element.hasClass('d-none')) {
            element.removeClass('d-none')
        } else {
            clone = element.clone()
            clone.val('')
            element.parent().append(clone)
        }
        return false
    })

    function populateEDandACfields(ele) {
        elevation_details = $(ele).parents('form').find('.elevation_details_input')

        elevation_details_value = $(ele).parents('form').find('.elevation-details').val()
        $(ele).parents('form').find('.elevation-details').each(function (index, element) {
            if (index != 0)
                elevation_details_value += ' &# ' + element.value
        })
        elevation_details.val(elevation_details_value)




        additional_cost = $(ele).parents('form').find('.additional_cost_input')

        additional_cost_value = $(ele).parents('form').find('.additional-cost').val()
        $(ele).parents('form').find('.additional-cost').each(function (index, element) {
            if (index != 0)
                additional_cost_value += ' &# ' + element.value
        })
        additional_cost.val(additional_cost_value)
        $(ele).parents('form').submit()
    }


    $(".edit_project_submit").on('click', function (event) {
        event.preventDefault()
        populateEDandACfields(this);
    })

    $('.submit-create-project-form').on('click', function (event) {
        event.preventDefault()
        populateEDandACfields(this);

    })


    drawings = {
        'Architect': [
            'Working drawing (floor plans)',
            'Designer wall details',
            'Filler slab layout',
            'Sections',
            '2 D elevation',
            'Door Window details, Window grill details',
            'Flooring layout details',
            'Toilet,kitchen Dadoing Details',
            'Compound wall details',
            'Fabrication details',
            'Sky light details',
            'External and Internal Paint Shades'
        ],
        'Structural': [
            'Column Marking',
            'Footing Layout',
            'UG sump details',
            'Plinth Beam layout',
            'Staircase details',
            'Floor form work ,beam and slab reinforcement details',
            'OHT slab details',
            'Lintel details.'
        ],
        'Electrical': [
            'Electrical', 'Conduit'
        ],
        'Plumbing': [
            'Water line drawings',
            'Drainage line drawings',
            'RWH Details'
        ]
    }

    $('#drawing_type').on('change', function () {
        type = $(this).val()
        if (type.length) {
            for (const drawing of drawings[type]) {
                $(".drawing_name_select").append($("<option></option>")
                    .attr("value", drawing)
                    .text(drawing))
            }
        }
    })

    $('#total_bua').on('keyup mouseup', function() {
        total_bua = $('#total_bua').val()
        if (parseFloat(total_bua) > parseFloat($('.total_bua_summation').text())) {
            alert('Total bua cannot be more than projects built up area summation')
            $('#total_bua').val(parseFloat($('.total_bua_summation').text()))
        }
        cost_per_sqft = $('#cost_per_sqft').val() 
        $('#wo_value').val((parseFloat(cost_per_sqft) & parseFloat(total_bua)).toString())
    })

    $('#cost_per_sqft').on('keyup', function() {
        total_bua = $('#total_bua').val()
        cost_per_sqft = $('#cost_per_sqft').val() 
        $('#wo_value').val((parseFloat(cost_per_sqft) * parseFloat(total_bua)).toString())
    })

    function showWorkOrderMilestone() {
        selected_trade = $("#trade").val().trim()

        if (selected_trade && $('.debit-note').length == 0) {
            if (['civil','electrical','painting','plumbing'].includes(selected_trade.toLowerCase())) {
                $('.bua-section').removeClass('d-none');
                $('.cost-per-sqft-section').removeClass('d-none');
                $('#wo_value').attr('readonly','readonly')
            } else {
                $('.bua-section').addClass('d-none');
                $('.cost-per-sqft-section').addClass('d-none');
                $('#wo_value').removeAttr('readonly')
            }
        } else {
            $("#stage").empty()
        }
        project_id = $(".work_order_project_select").val()
        contractor_id = $('.work-order-select-contractor').val()
        if (selected_trade && selected_trade.trim() === '' || project_id.trim() === '') return false;
        $('.milestones_section').find('.milestones_and_percentages_item').remove()
        $.ajax({
            url: '/get_wo_milestones_and_percentages',
            type: "POST",
            dataType: 'json',
            data: {
                'trade': selected_trade,
                'project_id': project_id,
                'contractor_id': contractor_id
            },
            success: function (data) {
                console.log(data)
                if (data['message'] == 'success') {
                    $('.error_message').addClass('d-none')
                    $('.milestones_section').removeClass('d-none')
                    $('.add-milestone-stage-btn').removeClass('d-none')
                    const milestones_and_percentages = data['milestones_and_percentages']
                    for (stage of Object.keys(milestones_and_percentages)) {
                        if($('.debit-note').length) {
                            $("#stage").append($("<option></option>")
                            .attr("value", stage)
                            .text(stage))
                        }                        
                    }
                } 
            }
        });
    }

    function showStandardMilestones() {
        selected_trade = $("#trade").val()

        if (selected_trade && $('.debit-note').length == 0) {
            if (['civil','electrical','painting','plumbing'].includes(selected_trade.toLowerCase())) {
                $('.bua-section').removeClass('d-none');
                $('.cost-per-sqft-section').removeClass('d-none');
                $('#wo_value').attr('readonly','readonly')
            } else {
                $('.bua-section').addClass('d-none');
                $('.cost-per-sqft-section').addClass('d-none');
                $('#wo_value').removeAttr('readonly')
            }
        } else {
            $("#stage").empty()
        }
        project_id = $(".work_order_project_select").val()
        if (selected_trade && selected_trade.trim() === '' || project_id.trim() === '') return false;
        $('.milestones_section').find('.milestones_and_percentages_item').remove()
        $.ajax({
            url: '/get_standard_milestones_and_percentages',
            type: "POST",
            dataType: 'json',
            data: {
                'trade': selected_trade,
                'project_id': project_id
            },
            success: function (data) {
                console.log(data)
                if (data['message'] == 'success') {
                    $('.error_message').addClass('d-none')
                    $('.milestones_section').removeClass('d-none')
                    $('.add-milestone-stage-btn').removeClass('d-none')
                    const milestones_and_percentages = data['milestones_and_percentages']
                    for (stage of Object.keys(milestones_and_percentages)) {
                        if($('.debit-note').length) {
                            $("#stage").append($("<option></option>")
                            .attr("value", stage)
                            .text(stage))
                        }
                        milestones_and_percentages_item = $('.milestones_and_percentages_item.template').clone()
                        milestones_and_percentages_item.removeClass('template')
                        milestones_and_percentages_item.find('.milestone-field').val(stage)
                        milestones_and_percentages_item.find('.percentage-field').val(milestones_and_percentages[stage])
                        milestones_and_percentages_item.removeClass('d-none')
                        $('.milestones_section').append(milestones_and_percentages_item)
                    }
                } else {
                    $('.error_message').text(data['message'])
                    $('.error_message').removeClass('d-none')
                    $('.milestones_section').addClass('d-none')
                    $('.add-milestone-stage-btn').addClass('d-none')
                }
            }
        });
    }

    function updateTradesForContractor() {
        contractor_id = $('.work-order-select-contractor').val()
        if (contractor_id.length) {
            $(".work-order-trade-select select").empty()
            $(".work-order-trade-select select").append($("<option></option>"))
            $.ajax({
                url: '/update_trades_for_contractor',
                type: "POST",
                dataType: 'json',
                data: { 'contractor_id': contractor_id },
                success: function (data) {
                    console.log(data)
                    for (const trade of data) {
                        if($(".work-order-trade-select select").length) {
                            $(".work-order-trade-select select").append($("<option></option>")
                            .attr("value", trade)
                            .text(trade))
                        } else {
                            $(".work-order-trade-select-debit-note select").append($("<option></option>")
                            .attr("value", trade)
                            .text(trade))
                        }
                        
                    }
                }
            });
        }
    }

    $('.work-order-select-contractor').on('change', updateTradesForContractor)
    $('.work_order_project_select').on('change', showStandardMilestones)
    $(".work-order-trade-select select").on('change', showStandardMilestones)
    $(".work-order-trade-select-debit-note select").on('change', showWorkOrderMilestone)
    $('.add-milestone-stage-btn').on('click', function () {
        milestones_and_percentages_item = $('.milestones_and_percentages_item.template').clone()
        milestones_and_percentages_item.removeClass('template')
        milestones_and_percentages_item.removeClass('d-none')
        $('.milestones_section').append(milestones_and_percentages_item)
        return false
    })

    $('.create_work_order_submit').on('click', function(e) {
        e.preventDefault();
        percentage = 0;
        $('.percentage-field').each(function(index, element) {
            if (element.value)
            percentage += parseFloat(element.value)
        })
        if (parseInt(percentage) != 100) {
            alert(`Percentages add up to ${percentage.toString()}. Percentages need to add up to 100`)
            return false;
        }
        $('.create_work_order_submit').parents('form').submit()
    })

    if($('.clear-individual-balance').length) {
        $('.clear-individual-balance').each(function(index, element) {
            if(parseInt($(element).parents('tr').find('.approved_amount').text()) == 0) return;
            amountDifference = parseInt($(element).parents('tr').find('.billed_amount').text()) - parseInt($(element).parents('tr').find('.approved_amount').text())
            if(amountDifference > 0) 
                $(element).removeClass('d-none')            
        })

        $('.force-open-to-clear-balance').each(function(index, element) {
            if(parseInt($(element).parents('tr').find('.approved_amount').text()) == 0) return;
            amountDifference = parseInt($(element).parents('tr').find('.billed_amount').text()) - parseInt($(element).parents('tr').find('.approved_amount').text())
            if(amountDifference > 0) 
                $(element).removeClass('d-none')            
        })

        $('.force-open-to-clear-balance').on('click', function(){
            if(confirm('Are you sure you want to open this bill to clear balance?')) {
                bill_id = $(this).parents('tr').find('.bill_id').text().trim()
                $.ajax({
                    url: '/force_open_clear_balance',
                    type: "POST",
                    dataType: 'json',
                    data: {
                    'bill_id': bill_id
                    },
                    success: function (data) {
                        window.location.reload()
                    }
                })
            }
        })

        $('.clear-individual-balance').on('click', function(){
            if($(this).text() != 'Clear balance') return;
            $(this).css('opacity','0.5')
            $(this).text('Clearing..')
            amountDifference = parseInt($(this).parents('tr').find('.billed_amount').text()) - parseInt($(this).parents('tr').find('.approved_amount').text())
            stageName = $(this).parents('tr').find('.stage').text().trim()
            bill_id = $(this).parents('tr').find('.bill_id').text().trim()
            contractor_name = $('.contractor_name').text()
            contractor_code = $('.contractor_code').text()
            contractor_pan = $('.contractor_pan').text()
            project_id = $('.project_id').text()
            trade =  $('.trade').text()
            work_order_id = $('.work_order_id').text()
            $.ajax({
                url: '/clear_individual_balance',
                type: "POST",
                dataType: 'json',
                data: {
                 'balance_amnt': amountDifference,
                 'contractor_name': contractor_name,
                 'contractor_code': contractor_code,
                 'contractor_pan': contractor_pan,
                 'project_id': project_id,
                 'trade': trade,
                 'work_order_id': work_order_id,
                 'stage': stageName,
                 'bill_id': bill_id

                },
                success: function (data) {
                    window.location.reload()
                }
            });
        })
    }

    $('.clear-balance-btn').on('click', function() {
        balance_amnt = parseInt($('.balance').text())
        if (balance_amnt) {
            contractor_name = $('.contractor_name').text()
            contractor_code = $('.contractor_code').text()
            contractor_pan = $('.contractor_pan').text()
            project_id = $('.project_id').text()
            trade =  $('.trade').text()
            work_order_id = $('.work_order_id').text()
            $.ajax({
                url: '/clear_wo_balance',
                type: "POST",
                dataType: 'json',
                data: {
                 'balance_amnt': balance_amnt,
                 'contractor_name': contractor_name,
                 'contractor_code': contractor_code,
                 'contractor_pan': contractor_pan,
                 'project_id': project_id,
                 'trade': trade,
                 'work_order_id': work_order_id,

                },
                success: function (data) {
                    window.location.reload()
                }
            });
        }
    })



});

function onInputNumberInt(value) {
    // handle validations
    // allow value to be positive number only
    // use this helper on every int data type 
    value = value.replace(/[^0-9]/g, '');
    return value;

}

function onInputNumberFloat(value) {
    // handle validations
    // allow value to be positive number only
    // use this helper on every float data type 

    if (isNaN(value)) {
        value = value.replace(/[^0-9\.]/g, '');
        if (value.split('.').length > 2)
            value = value.replace(/\.+$/, "");
    }
    return value;

}


function handleNoOfFloorsChange(value) {
    // if value is G+1 then set sf_slab_area and tf_slab_area to 0
    // if value is G+2 then set tf_slab_area to 0
    if (value == 'G + 1') {
        $('#sf_slab_area').val(0);
        $('#tf_slab_area').val(0);
    } else if (value = 'G + 2') {
        $('#tf_slab_area').val(0);
    }
}


function validateForm() {
    let x = document.forms["myForm"]
    let isValid = true;
    let no_of_floors = x["no_of_floors"].value ? x["no_of_floors"].value : '';
    let floor_options = ['G + 1', 'G + 2', 'G + 3', 'G + 4','G + 5','G + 6'];
    for (let i = 0; i < x.length; i++) {
        switch (x[i].id) {
            case ("project_number"):
                if (x[i].value == "") {
                    document.getElementById("project_number_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("project_number_error").setAttribute("class", "d-none");
                }
                break;
            case ("project_name"):
                if (x[i].value == "") {
                    document.getElementById("project_name_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("project_name_error").setAttribute("class", "d-none");
                }
                break;
            case ("project_location"):
                if (x[i].value == "") {
                    document.getElementById("project_location_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("project_location_error").setAttribute("class", "d-none");
                }
                break;
            case ("no_of_floors"):
                if (x[i].value == "") {
                    document.getElementById("no_of_floors_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("no_of_floors_error").setAttribute("class", "d-none");
                }
                break;
            case ("package_type"):
                if (x[i].value == "") {
                    document.getElementById("package_type_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("package_type_error").setAttribute("class", "d-none");
                }
                break;
            case ("date_of_initial_advance"):
                if (x[i].value == "") {
                    document.getElementById("date_of_initial_advance_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("date_of_initial_advance_error").setAttribute("class", "d-none");
                }
                break;
            case ("date_of_agreement"):
                if (x[i].value == "") {
                    document.getElementById("date_of_agreement_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("date_of_agreement_error").setAttribute("class", "d-none");
                }
                break;
            case ("sales_executive"):
                if (x[i].value == "") {
                    document.getElementById("sales_executive_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("sales_executive_error").setAttribute("class", "d-none");
                }
                break;
            case ("site_area"):
                if (x[i].value == "") {
                    document.getElementById("site_area_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("site_area_error").setAttribute("class", "d-none");
                }
                break;
            case ("paid_percentage"):
                if (x[i].value == "") {
                    document.getElementById("paid_percentage_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("paid_percentage_error").setAttribute("class", "d-none");
                }
                break;
            case ("project_value"):
                if (x[i].value == "") {
                    document.getElementById("project_value_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("project_value_error").setAttribute("class", "d-none");
                }
                break;
            case ("cost_sheet"):
                if (x[i].files.length == 0) {
                    document.getElementById("cost_sheet_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("cost_sheet_error").setAttribute("class", "d-none");
                }
                break;
            case ("site_inspection_report"):
                if (x[i].files.length == 0) {
                    document.getElementById("site_inspection_report_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("site_inspection_report_error").setAttribute("class", "d-none");
                }
                break;
            case ("agreement"):
                    if (x[i].files.length == 0) {
                        document.getElementById("agreement_error").setAttribute("class", "error");
                        isValid = false;
                    }
                    else {
                        document.getElementById("agreement_error").setAttribute("class", "d-none");
                    }
                    break;
            case ("shr_oht"):
                if (x[i].value == "") {
                    document.getElementById("shr_oht_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("shr_oht_error").setAttribute("class", "d-none");
                }
                break;
            case ("gf_slab_area"):
                if (floor_options.includes(no_of_floors) && x[i].value == "") {
                    document.getElementById("gf_slab_area_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("gf_slab_area_error").setAttribute("class", "d-none");
                }
                break;
            case ("ff_slab_area"):
                if (floor_options.includes(no_of_floors) && x[i].value == "") {
                    document.getElementById("ff_slab_area_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("ff_slab_area_error").setAttribute("class", "d-none");
                }
                break;
            case ("sf_slab_area"):
                if (floor_options.includes(no_of_floors) && x[i].value == "") {
                    document.getElementById("sf_slab_area_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("sf_slab_area_error").setAttribute("class", "d-none");
                }
                break;
            case ("tf_slab_area"):
                if (floor_options.includes(no_of_floors) && x[i].value == "") {
                    document.getElementById("tf_slab_area_error").setAttribute("class", "error");
                    isValid = false;
                }
                else {
                    document.getElementById("tf_slab_area_error").setAttribute("class", "d-none");
                }
                break;

        }
        document.getElementById('create_project_submit').disabled = isValid;
    }
    return isValid;
}

