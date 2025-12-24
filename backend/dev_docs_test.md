# Batch API
**Link**: https://developer.isams.com/isams-developer-documentation/docs/batch-api

# Batch API

Use Batch API Keys if you want to:

- Apply the highest level of access control to third parties and internal school developers.
- Control the amount and type of data accessed. This applies to data flowing in and out of your iSAMS system.
- Enable large amounts of data to be requested from iSAMS in a single hit. This is not possible with other types of API key.

> 📘By their nature, batch API keys cannot be used for real time data.

Choose to:

- Create a Batch API Key. This function is only available for iSAMS Administrator users.
- Request a Batch API Key. Your request is sent to iSAMS.
- Edit a Batch API Key.
- Update IP Restrictions for a Batch API Key.
- Update Domain Restrictions for a Batch API Key.
- Delete a Batch API Key.
- View Batch API Key Requests.
- Delete Batch API Key Request Logs..
- Manage Batch API Logging.

Updated almost 6 years ago


---

# Batch API Keys
**Link**: https://developer.isams.com/isams-developer-documentation/docs/batch-api-keys

# Batch API Keys

From the API Key to the Product Name, find out more about each of the properties that a single Batch API key contains.

Batch API Keys are created by the school - they can create an unlimited amount. For the purpose of logging and security, we recommend one key per integration.

A Batch API key contains the following properties:

Associated with a Batch API key are Batch SQL Methods - a Batch API key must have at least one method. There is no limit to the number of methods that can be allocated to a single Batch API key.

> 📘We recommend using a single Batch API key in conjunction with Batch Method Filtering which you can read about in more detail within the "Applying Method Filters to a Batch API Request" section within the Filtering Data documentation.

Updated almost 6 years ago


---

# Filtering Data
**Link**: https://developer.isams.com/isams-developer-documentation/docs/batch-api-filtering

# Filtering Data

To make the generating, transport and processing of XML files as seamless as possible, use this documentation to apply filters to the Batch API request.

Certain Batch SQL Methods can return huge amounts of data which can have an effect on the generation, transport, and processing of the XML. To ease this problem, we have added basic required filters to specific SQL Methods. This allows developers to filter by date ranges, or exclude certain data they may have already processed or synchronised.

> 🚧If a method requires filters, then at least one of the filters must be added to the request.

The XML document contains the filters for the SQL Methods you wish to filter. The syntax is provided below - you only need to include filters that are relevant to the SQL Methods which were selected when configuring the API key.

When the request is received, the Batch API Service will check the filters and parse the XML. If the XML is valid, it will append the filter nodes to the underlying SQL query and return the XML with the filters applied.

> 📘Only a small number of SQL Methods support filtering; they are shown in the "Example POST request" section below.

## Applying Filters to the Batch API Request

The XML for the filters should be created as follows (replace the ModuleName and MethodName nodes with module and method names in the "Example POST request" section below):

```
<?xml version="1.0" encoding="utf-8" ?>
<Filters>
         <ModuleName>
                 <MethodName StartDate="2012-08-16" EndDate="2013-03-23" />
         </ModuleName>
</Filters>
```

This must be sent as a POST request with the Content-Type header set to application/xml.

In order to test sending requests to the Batch API and viewing the responses, we would recommend the Postman app which can be found at the following URL: https://www.getpostman.com/

It can either be sent with the body as a binary file containing the XML or with the XML itself in the body.

## Applying Method Filters to a Batch API Request

Historically, due to the quantity and size of the data that can be returned by the Batch API, iSAMS has always recommended requesting multiple API keys in order to reduce the chance of timeouts. However, there is now support to use a single API key and supply filters against the methods selected for a particular API key. The methods to run should be specified within the filters sections of the POST request body; e.g.

```
<?xml version="1.0" encoding="utf-8" ?>
<Filters>
    <MethodsToRun>
        <Method>SchoolReports_GetReports</Method>
        <Method>Pupil_GetApplicants</Method>
    </MethodsToRun>
    <SchoolReports>
        <Reports reportCycleIdsToInclude="9322,9323"/>
    </SchoolReports>
</Filters>
```

Only the methods specified in the MethodsToRun section will be invoked. If this section is not included, it will invoke all methods allocated to the API key.

The method names can be found within the table on the Example Responses page. If you supply a method name that does not exist or is not associated with this API key, you'll receive a 403 response; e.g.

```
<?xml version="1.0" encoding="utf-16"?>
<Message>
    <MessageId>MethodsNotAllocatedToKeyException</MessageId>
    <MessageName>MethodsNotAllocatedToKeyException</MessageName>
    <Title>Methods Not Allocated To Key</Title>
    <Description>The following methods specified in the MethodsToRun filter are not allocated to the requested key: pupil_getapplicant</Description>
</Message>
```

> 📘Please focus on reducing the number of API keys you use so when it comes to needing the Client ID and Client Secret to authenticate your requests, schools will only need to re-generate a single API key.

## Example POST Request

Displayed below is an example of the XML that needs to be sent via within the POST body; the request below will filter:

- Calendar - Eventsmethod to only return authorised events between 16th August 2012 and 23rd March 2013.
- Cover Manager - Lesson Suspensionsmethod to only return lesson suspensions between 16th August 2012 and 23rd March 2013.
- Cover Manager - Room Closuresmethod to only return room closures between 16th August 2012 and 23rd March 2013.
- Daily Bulletin - Bulletinsmethod to only return authorised items for 22nd December 2010.
- Discipline Manager - Detentionsmethod to only return authorised detentions between 28th September 2013 and 23rd December 2013.
- Exams Manager - Exam Results (Filtered)method to only return exam results that match the cycle IDs 52, 53 & 54.
- Student Manager - Contacts (Advanced)method to only return student contacts which have a Contact Type of "Mother" or "Father", are set as Contact Only, whose Contact Location is set to "Work" or "Company", whose address isnotthe student's home address, the student's system status is 1 or 0, and the student's admissions status is "Accepted" or "Denied" and the student's enrolment school year is 2017 or 2018.
- Student Manager - Contacts (Advanced with Custom Fields)method to only return student contacts which have a Contact Type of "Mother" or "Father", are set as Contact Only, whose Contact Location is set to "Work" or "Company", whose address isnotthe student's home address, the student's system status is 1 or 0, where the student's admissions status is "Accepted" or "Denied" and the student's enrolment school year is 2017 or 2018.
- Student Manager - Passportsmethod to only return passport data for students that match the system statuses of 0 or 1.
- Student Manager - Custom Pupil Group Membership Items (Filtered)method to return student group membership items that match the system statuses of 0 or 1.
- Pupil Registers - Free School Mealsmethod to only return date and time records between 28th January 2013 and 13th February 2013.
- Pupil Registers - Gifted and Talented Registermethod to only return gifted and talented records for students with system status -1 or 1.
- Pupil Registers - SEN DfE Recordsmethod to only return SEN DfE records for students with system status 0 or 1.
- Pupil Registers - SEN Lessonsmethod to only return SEN lesson records for students with system status 0 or 1.
- Pupil Registers - SEN Registermethod to only return SEN register records for students with system status 0 or 1.
- Pupil Registers - SEN Typesmethod to only return SEN types for students with system status 0 or 1.
- Registrations Manager - Out Of Schoolmethod to only return out of school records between 25th February 2013 and 2nd April 2013.
- Registrations Manager - Registration Periodsmethod to only return registration records between 1st March 2013 and 1st June 2013.
- Registrations Manager - Registration Statusesmethod to only return registration records between 21st May 2013 and 22nd September 2013.
- Rewards and Conduct - Recordsmethod to only return authorised Rewards and Conduct records between 28th September 2013 and 23rd December 2013.
- School Reports - Recordsmethod to only return reporting records that match the cycle IDs - 2, 3, 5, 7, 11, 13, 17 & 19.
- School Reports - Report Cyclesmethod to only return incomplete report records that match the cycle IDs 3 & 9 for students in year 13.
- School Reports - Report Cycle Detailsmethod to only return report cycles in term 1 of 2016.
- Tracking Manager - External Datamethod to only return external data records that match the report IDs 1, 2, 4, 6, 8, 12, 16 & 18.

```
<?xml version="1.0" encoding="utf-8" ?>
<Filters>
	<Calendar>
		<Events StartDate="2012-08-16" EndDate="2013-03-23" />
	</Calendar>
	<CoverManager>
		<AllLessonSuspensions StartDate="2012-08-16" EndDate="2013-03-23" />
		<AllRoomClosuresAndCover StartDate="2012-08-16" EndDate="2013-03-23" />
	</CoverManager>
	<DailyBulletin>
		<DailyBulletins StartDate="2010-12-22" EndDate="2013-03-23" />
	</DailyBulletin>
	<ExamsManager>
		<ExamResultsFiltered ExamCycleIdsToInclude="52,53,54" /> 
	</ExamsManager>
	<Discipline>
		<Detentions StartDate="2013-09-28" EndDate="2013-12-23" />
	</Discipline>
	<StudentManager>
		<Contacts ContactTypes="Mother,Father" ContactOnly="true" ContactLocations="Work,Company" StudentHome="false" SystemStatusesToInclude="0,1" AdmissionsStatusesToInclude="Denied,Accepted" EnrolmentSchoolYearsToInclude="2017,2018" />
		<ContactsWithCustomFields ContactTypes="Mother,Father" ContactOnly="true" ContactLocations="Work,Company" StudentHome="false" SystemStatusesToInclude="0,1" AdmissionsStatusesToInclude="Denied,Accepted" EnrolmentSchoolYearsToInclude="2017,2018" />   
		<CustomPupilGroupMembershipFiltered SystemStatusesToInclude="0,1" />
		<Passports SystemStatusesToInclude="0,1" />
	</StudentManager>
	<PupilRegisters>
		<FreeSchoolMeals StartDate="2013-01-28" EndDate="2013-02-13" />
		<GiftedAndTalentedRegister systemStatusesToInclude="-1,1" />
		<SENDfERecords systemStatusesToInclude="0,1" />
		<SENLessons systemStatusesToInclude="0,1" />
		<SENRegister systemStatusesToInclude="0,1" />
		<SENTypes systemStatusesToInclude="0,1" />
	</PupilRegisters>
	<Registration>
		<OutOfSchoolPupils StartDate="2013-02-25" EndDate="2013-04-02" />
		<RegistrationPeriods StartDate="2013-03-01" EndDate="2013-06-01" />
		<RegistrationStatus StartDate="2013-05-21" EndDate="2013-09-22" />
	</Registration>
	<RewardsAndConduct>
		<Records StartDate="2013-09-28" EndDate="2013-12-23" />
	</RewardsAndConduct>
	<SchoolReports>
		<Records IDsToInclude="2,3,5,7,11,13,17,19" />
		<ReportCycles ReportTerm="1" ReportCycleType="0" ReportYear="2016" />
		<Reports reportCycleIdsToInclude="3,9" ncYear="13" reportType="7" reportStatus="3" />
	</SchoolReports>
	<TrackingManager>
		<ExternalData IDsToInclude="1,2,4,6,8,12,16,18" />
	</TrackingManager>
</Filters>
```

Updated over 2 years ago


---

# Batch API Object Nodes
**Link**: https://developer.isams.com/isams-developer-documentation/docs/batch-api-object-nodes

# Batch API Object Nodes

Learn about the Batch API Object Nodes, including those within the HR Manager and Student Manager modules.

Updated almost 6 years ago


---

# Batch API FAQs
**Link**: https://developer.isams.com/isams-developer-documentation/docs/batch-api-faqs

# Batch API FAQs

Find the answers to some of the most frequently asked questions we receive surrounding our Batch APIs.

## Which methods are included in the "Batch API Core" that is available on the Developer Free plan?

The Batch API Core consists of the following methods:

Current Pupils
Siblings
Student Contacts
Current Staff
School Divisions
Academic Houses
Boarding Houses
Years
Forms
Pastoral Tutors
Terms

If you require other methods for your integration, please contact our Integrations Manager at partners@isams.com to discuss upgrade options.

## Clarification for interpretation of the iSAMS parental responsibility field

We are aware that there has been some confusion about the value being returned for the parental responsibility field for student contacts.

To clarify how the data should be interpreted, our development team has provided the following guidance:

The 'Contacts' BATCH API method will only return 'Yes' or 'No' for the parental responsibility if the contact has explicitly had the parental responsibility overwritten from the default value (The parental responsibility drop down for the contact has been changed from the default value to 'Yes' or 'No' and saved in iSAMS).

If this has not happened, then it will return 'Default'.

When ‘Default’ is returned from the 'Contacts' method, integrators should use the Control Panel 'Contact Types' method to get the default parental responsibility for the contact type associated with the contact. This method is documented here: Contact Types

## A key field or dataset is missing from a Batch API method

If you feel a field is missing from a method or a chunk of data is not provided, please raise the issue with our Integrations Manager: partners@isams.com.

## A client school has created a Batch API key and defined the methods - what's the web address of the XML feed?

The web address of the feed will be: https:///api/batch/1.0/xml.ashx?apiKey= and should look like this: https://developerdemo.isams.cloud/api/batch/1.0/xml.ashx?apiKey=0A1C996B-8E74-4388-A3C4-8DA1E40ADA57

## How often does the Batch XML feed update?

The school can define a cache time for each Batch API key. It defaults to 24 hours.  Please refer to the Caching, Limits & Throttling documentation.

## I require lots of data methods and the XML feed/request is huge - can I reduce it?

Any Batch API request can supply filters on the methods executed and therefore the data returned. Please refer to the "Applying Method Filters to a Batch API Request" section within the Filtering Data documentation.

## I'm having difficulties applying filters when requesting data via the Batch API, how should the request be formed?

Please refer to the Filtering Data documentation for detailed instructions on how to add filters to a request.

Alternatively, you can see how to construct the XML using the Example Application.

## How does the Batch API handle errors?

The Batch API returns the appropriate HTTP response code, depending on the nature of the error, along with further details in the XML response body.  Please refer to the Status Codes & Messages documentation.

## Why am I not getting as many records being returned as I expected?

Schools have an option to apply filters on a Batch API key for many of the methods.  Please check with the school to see if they have applied any of these filters.  If no filters have been applied on the Batch API key you are using, but you still believe that there are records missing from the response, please contact iSAMS Support.

## Why am I not getting all the Custom Fields returned?

Due to the sheer size and variation of use, the Custom Fields returned are filtered to the following:

- For ApplicantsGeneralContacts
- For StudentsGeneralContactsSchoolEnrolmentCensus
- For Student ContactsAll Contacts
- For Student HealthAll Health
- For Student TransportAll Transport
- For Employees/StaffGeneral > Core Staff Details & Personal DetailsSchool > Association & Contact & Location DetailsRoles

The REST API, however, does not have this restriction because it supports paging.

## How do I prevent sniffing attacks?

The Batch API can be configured to require a secure, encrypted connection to prevent such attacks. Please refer to the "SSL Restrictions" section within the Restrictions & Security documentation.

## Multiple requests are being made from an unrecognised domain or IP address - what can I do to protect against this?

The Batch API can be configured to restrict requests to those from a certain range of IP addresses or from specific domains.  It can also be configured to limit the number of requests which can be made in a given timeframe.  Please refer to "Domain and IP Address Restrictions" section in the Restrictions & Security documentation and also the "Rate Limits & Throttling" section in the Caching, Limits & Throttling documentation.

## How do I create a new Batch API key?

This will need to be requested and, once created, configured by an iSAMS administrator from within the iSAMS Control Panel.  Please refer to the Create a Batch API Key documentation.

## How do I change the data which is returned from a Batch API key?

This will need to be configured by an iSAMS administrator in the iSAMS Control Panel.  Please refer to the Edit a Batch API Key documentation.

## Can the Batch API be used to write data into iSAMS?

The Batch API is designed to allow data to be read in bulk from iSAMS and it is not possible to use the Batch API to write data to the iSAMS database.  A full REST API is in development to allow this functionality.

## How can I create a Batch API key to allow downloading of staff and student photos?

In order to use the endpoints for staff and student photos, you will need to generate a Batch API key with the relevant method selected.  This can then be used to perform the photo download.  For further details, please refer to the Photos documentation.

Updated over 3 years ago


---

