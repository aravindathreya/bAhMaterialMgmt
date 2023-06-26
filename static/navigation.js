$(document).ready(function () {

    function initRedirects() {
        console.log('initRedirects')
        setTimeout(() => {
            if(window.location.href.includes('view_users') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'view_users'
                $('.view_users_nav_btn').trigger('click')
            } else if(window.location.href.includes('view_vendors') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'view_vendors'
                $('.view_vendors_nav_btn').trigger('click')
            } else if(window.location.href.includes('enter_material') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'enter_material'
                $('.enter_material_nav_btn').trigger('click')
            } else if(window.location.href.includes('view_qs_approval_indents') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'view_qs_approval_indents'
                $('.view_qs_approval_indents_nav_btn').trigger('click')
            } else if(window.location.href.includes('view_approved_indents') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'view_approved_indents'
                $('.view_approved_indents_nav_btn').trigger('click')
            } else if(window.location.href.includes('view_approved_POs') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'view_approved_POs'
                $('.view_approved_POs_nav_btn').trigger('click')
            } else if(window.location.href.includes('view_ph_approved_indents') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'view_ph_approved_indents'
                $('.view_ph_approved_indents_nav_btn').trigger('click')
            } else if(window.location.href.includes('kyp_material') && window.currentTab == null && $('.nav-link.active').length == 0) {
                window.currentTab = 'kyp_material'
                $('.kyp_for_material_nav_btn').trigger('click')
            } else {
                window.currentTab = null;
            }

        },0)
    }        
        
    

    initRedirects();
    
    function initViewContractors() {
        if($('.contractor-profile-picture').length) {
            $('.contractor-profile-picture').each(function(index, element){
                const src = $(element).attr('data-src')
                $(element).attr('src', src)
            })
        } 
    }

    function initSearchProject() {
        console.log('initSearchProject')
        $('.search-project-field').on('keydown', function() {
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
    }

    function initBlockProject() {
        $('.block-project').on('click', function() {
            project_id = $(this).attr('data-project-id')
            $('.project_id').val(project_id)
        })
    }

    function initKypMaterial() {
        // $("#update_kyp_material").on('click', function(){
        //     const project = $("#project").val()
        //     if (project.length) {
        //         $.ajax({
        //             url: '/kyp_material?project_id='+project.toString(),
        //             type: "GET",        
        //             success: function (data) {     
        //                 $('.main-wrapper').html(data);
        //                 $('.main-wrapper').css('background','#e4e4e4')
        //                 $('.select2').select2();
        //         initRedirects()
        //                 initKypMaterial();
        //                 $('.select2').on('click', function(){
        //                     setTimeout(() => {
        //                         if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
        //                     }, 0)
        //                 })
        //             },
        //         });
        //     }
        // })
    }

    function initViewInventory() {
        // $('#get_procurement').on('click', function(){
        //     const project = $("#project").val()
        //     const material = $("#material").val()
        //     if(project.length && material.length) {
        //         $.ajax({
        //             url: '/view_inventory?project_id='+project.toString()+'&material='+material.toString(),
        //             type: "GET",        
        //             success: function (data) {        
        //                 $('.main-wrapper').html(data);
        //                 $('.main-wrapper').css('background','#e4e4e4')
        //                 $('.select2').select2();
        //         initRedirects()
        //                 initViewInventory();
        //                 $('.select2').on('click', function(){
        //                     setTimeout(() => {
        //                         if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
        //                     }, 0)
        //                 })
        //             },
        //         });
        //     }
        // })

        if($('#total_item_quantity').length) {
            let current_quantity = 0;
            let total_quantity = parseFloat($('#total_item_quantity').text().trim())
            $('.item_quantity').each(function(index, element){
                current_quantity += parseFloat($(this).text().trim())
            })
            let balance = total_quantity - current_quantity;
            $('#total_current_quantity').text('Current : '+current_quantity.toString())
            $('#total_balance_quantity').text('Balance : '+balance.toString())
        }
        
        if($('.item_difference_cost').length) {
            let total_cost = 0;
            $('.item_cost').each(function(index, element){
                total_cost += parseFloat($(this).text().trim())
            })
            $("#total_cost").text(total_cost)
        
            let total_difference_cost = 0;
            $('.item_difference_cost').each(function(index, element){
                total_difference_cost += parseFloat($(this).text().trim())
            })
            $("#total_difference_cost").text(total_difference_cost)
        }
    }

    function calcAmount() {
        const quantity = $('#quantity').val().trim()
        const rate = $("#rate").val().trim()
        const gst = $("#gst").val()
        const loading_unloading = $('#loading_unloading').val()
        const transportation = $('#transportation').val()
        const amount = parseFloat(rate) * parseFloat(quantity) 
        const total = ((gst / 100 ) * amount) + amount;
        const total_with_other_expenses = total + parseFloat(loading_unloading) + parseFloat(transportation)
        $("#total_amount").val(total_with_other_expenses)
    }

    function initEnterMaterial() {
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
        
        
        $("#gst").on("change",  calcAmount)
        $("#rate").on("keyup", calcAmount)
        $("#quantity").on("keyup", calcAmount)
        $("#transportation").on("keyup", calcAmount)
        $("#loading_unloading").on("keyup", calcAmount)
    }

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
                        $(".work-order-trade-select select").append($("<option></option>")
                            .attr("value", trade)
                            .text(trade))
                    }
                }
            });
        }
    }
    

    function initCreateWorkorder() {
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
        $(".work_order_project_select").on('change', function () {
            const project_id = $(this).val()
            if (project_id) updateSlabArea(project_id)
        })
        showStandardMilestones()
        $('.work-order-select-contractor').on('change', updateTradesForContractor)
        $(".work-order-trade-select select").on('change', showStandardMilestones)
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
    }
    


    $('.create_project_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/create_project',
            type: "GET",        
            success: function (data) {         
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.unapproved_projects_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/unapproved_projects',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.archived_projects_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/archived_projects',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.projects_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/projects',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                initSearchProject()
                initBlockProject()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()                        
                    }, 0)
                })
            },
        });
    })

    $('.create_user_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/create_user',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_users_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_users',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })


    $('.vendor_registration_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/vendor_registration',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_vendors_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_vendors',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    
    $('.kyp_for_material_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/kyp_material',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                initKypMaterial();
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.enter_material_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/enter_material',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                initEnterMaterial();
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.shifiting_entry_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/shifting_entry',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_inventory_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_inventory',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                initViewInventory();
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_qs_approval_indents_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_qs_approval_indents',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_approved_indents_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_approved_indents',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_approved_POs_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_approved_POs',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    
    $('.view_ph_approved_indents_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_ph_approved_indents',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })
    
    $('.view_deleted_indents_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_deleted_indents',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.contractor_registration_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/contractor_registration',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.view_contractors_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/view_contractors',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                initViewContractors()
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    $('.create_work_order_nav_btn').on('click', function(){
        $('.nav-link').removeClass('active');
        $(this).addClass('active');        
        $('.main-wrapper').html('')
        $(".main-wrapper").css({background:'linear-gradient(90deg, rgba(173,173,173,1) 0%, rgba(255,255,255,1) 70%)'});
        $.ajax({
            url: '/create_work_order',
            type: "GET",        
            success: function (data) {        
                $('.main-wrapper').html(data);
                $('.main-wrapper').css('background','#e4e4e4')
                $('.select2').select2();
                initRedirects()
                initCreateWorkorder();
                $('.select2').on('click', function(){
                    setTimeout(() => {
                        if($('.select2-search__field').length) $('.select2-search__field').get(0).focus()
                    }, 0)
                })
            },
        });
    })

    


    
    
    
    
    
    
    
    

    

    

    
    
    

});