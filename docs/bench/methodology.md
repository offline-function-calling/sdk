Our benchmark evaluates models against the following 15 parameters, which are tested across the scenarios listed below. You can view the leaderboard [here](./leaderboard.md).

### Parameters

!!! note "`function-discovery`"

    &nbsp;The model must identify and catalog available functions from specifications in the conversation history, including user-provided and self-generated functions.

!!! note "`function-selection`"

    &nbsp;The model must select the correct function(s) from the list of discovered functions to accomplish a certain task, avoiding hallucination of non-existent tools.

!!! note "`parameter-extraction`"

    &nbsp;The model must extrapolate appropriate pieces of information from the conversation to use as arguments when calling a function, taking note of the expected types, formats, and required parameters.

!!! note "`parameter-transformation`"

    &nbsp;The model must transform user input from natural language or other formats into the precise data types and structures required by the function's arguments.

!!! note "`function-calling`"

    &nbsp;The model must be able to produce valid, executable function calls that conform to the defined API, with correctly named parameters and formatted arguments.

!!! note "`output-understanding`"

    &nbsp;The model must make use of the data returned by a function to generate helpful, user-friendly responses and inform subsequent actions.

!!! note "`parallel-calling`"

    &nbsp;The model must identify when multiple independent function calls can be made concurrently, and support receiving their outputs out of order.

!!! note "`composite-calling`"

    &nbsp;The model must be able to plan ahead and chain function calls in sequence, where the output of one function is used as the input for the next.

!!! note "`context-application`"

    &nbsp;The model must be able to use information from earlier in the conversation, including user prompts and previous function call outputs, for subsequent tasks.

!!! note "`error-handling`"

    &nbsp;The model must be able to handle errors returned by a function, understand why the error occurred, and decide on a suitable course of action such as retrying or informing the user.

!!! note "`missing-functions`"

    &nbsp;The model must be able to identify when it does not have access to an appropriate function to fulfill a request and inform the user about this limitation.

!!! note "`missing-parameters`"

    &nbsp;The model must identify when it lacks a piece of information required to call a function, and ask the user instead of making an assumption.

!!! note "`handling-ambiguity`"

    &nbsp;When faced with a vague request, the model must ask the user about their intent or the specific entities involved, rather than guessing.

!!! note "`constraint-adherence`"

    &nbsp;The model must adhere to arbitrary constraints imposed by the user or the environment, such as being told not to use a certain function to perform a task.

!!! note "`function-generation`"

    &nbsp;The model must be able to generate function code and specifications based on a user's request, and then subsequently use that new function in the conversation.

### Scenarios

**Simple Function Call**
<br /><small> `function-discovery` `parameter-extraction` `function-calling` </small>

!!! info "`functions`"

        :::python
        get_pr_details(repo: str, pr_number: int) -> dict

!!! note "`question`"

    &nbsp;What's the status of PR #1138 in the 'frontend' repo?

!!! warning "`expected`"

    &nbsp;The model should identify the single available function, extract the string 'frontend' and the integer '1138' directly from the text, and execute a correct function call.

<br/> <hr />

**Parameter Extraction**
<br /><small> `parameter-transformation` `function-calling` </small>

!!! info "`functions`"

        :::python
        create_deployment(app_name: str, version: str, replicas: int, memory_mb: int) -> dict

!!! note "`question`"

    &nbsp;Deploy the 'analytics-service' app version 'v2.1.0' with 3 replicas and 512MB memory.

!!! warning "`expected`"

    &nbsp;The model should correctly identify and extract all parameters. It must convert the string '512MB' into the integer `512` to match the function's type signature.

<br/> <hr />

**Parameter Transformation**
<br /><small> `parameter-transformation` `function-calling` </small>

!!! info "`functions`"

        :::python
        schedule_backup(database_name: str, schedule_cron: str, retention_days: int) -> dict

!!! note "`question`"

    &nbsp;Schedule a backup for the 'orders' database every day at 2 AM, and keep backups for 2 weeks.

!!! warning "`expected`"

    &nbsp;The model must transform the natural language inputs into the required formats. It should convert 'every day at 2 AM' into the cron string `0 2 * * *` and '2 weeks' into the integer `14`.

<br/> <hr />

**Resolving Ambiguous Function Choice**
<br /><small> `function-selection` `handling-ambiguity` `parameter-transformation` </small>

!!! info "`functions`"

        :::python
        search_products(query: str, category: str = None, price_range: tuple = None, brand: str = None, rating_min: float = None) -> list
        filter_products(product_ids: list, filters: dict) -> list
        get_product_recommendations(user_id: str, category: str = None, price_max: float = None) -> list
        get_similar_products(product_id: str, similarity_threshold: float = 0.7) -> list

!!! note "`question`"

    &nbsp;Find me some wireless headphones under $100 with good reviews.

!!! warning "`expected`"

    &nbsp;The model should select `search_products` and properly infer parameters: `query="wireless headphones"`, `price_range=(0, 100)`, and `rating_min=4.0` (inferred from "good reviews"). It must recognize that `filter_products` requires existing product IDs, `get_product_recommendations` needs a user_id, and `get_similar_products` needs a reference product - none of which are available.

<br/> <hr />

**Stateful Composite Calling**
<br /><small> `composite-calling` `context-application` `output-understanding` </small>

!!! info "`functions`"

        :::python
        get_document_status(doc_id: str) -> dict
        submit_for_review(doc_id: str, reviewer_id: str) -> dict
        approve_document(doc_id: str, approver_id: str) -> dict

!!! note "`question`"

    &nbsp;Move document 'DOC-001' to the next stage in the approval workflow.

!!! warning "`expected`"

    &nbsp;The model must first call `get_document_status` to determine the current state. Based on the output, it should then select and call the correct subsequent function (e.g., `submit_for_review` or `approve_document`).

<br/> <hr />

**Parallel Function Calling**
<br /><small> `parallel-calling` `output-understanding` `parameter-transformation` </small>

!!! info "`functions`"

        :::python
        crm_get_customer(customer_id: str) -> dict
        billing_get_invoices(customer_id: str) -> list
        support_get_tickets(customer_id: str) -> list
        merge_customer_profile(crm_data: dict, billing_data: list, support_data: list) -> dict

!!! note "`question`"

    &nbsp;Give me a complete profile for customer 'CUST-789' across all systems.

!!! warning "`expected`"

    &nbsp;The model should recognize the need to gather data from multiple systems. It must make parallel calls to `crm_get_customer`, `billing_get_invoices`, and `support_get_tickets`, then use the collected data to call `merge_customer_profile`.

<br/> <hr />

**Cascading Error Recovery**
<br /><small> `error-handling` `composite-calling` `function-selection` </small>

!!! info "`functions`"

        :::python
        get_user_from_cache(user_id: str) -> dict
        get_user_from_database(user_id: str) -> dict
        get_user_from_ldap(username: str) -> dict

!!! note "`question`"

    &nbsp;Get user details for user_id 'u-999'.
    <small>*Scenario: Cache returns not_found, then database returns connection_error.*</small>

!!! warning "`expected`"

    &nbsp;The model must demonstrate a robust error handling chain. After the cache fails, it should attempt the database. When the database fails, it must not give up but instead ask the user for more information (`username`) to try the next available tool (`get_user_from_ldap`).

<br/> <hr />

**Adhering to Contextual Constraints**
<br /><small> `constraint-adherence` `function-selection` `context-application` </small>

!!! info "`functions`"

        :::python
        view_sensitive_data(resource_id: str) -> dict  # Requires level-3 clearance
        view_summary_data(resource_id: str) -> dict   # Requires level-2 clearance

!!! note "`question`"

    &nbsp;Show me the data for resource 'RES-001'.
    <small>_(the user has level-2 clearance)_</small>

!!! warning "`expected`"

    &nbsp;The model must understand the user's permission level from the conversational context. It should treat this as an implicit constraint, filter the available functions, and select `view_summary_data` as the only permissible tool.

<br/> <hr />

**Dynamic Function Generation**
<br /><small> `function-generation` `function-discovery` `parameter-transformation` `parallel-calling`</small>

!!! info "`functions`"

        (None provided initially)

!!! note "`question`"

    &nbsp;I need to score incoming leads. Can you write a Python function to calculate a `lead_score` from a user dictionary? Give +10 points if the `job_title` is "Software Engineer", +5 if `country` exists, and +20 if `company_size` is over 1000.

!!! note "`followup`"

    Score a lead on the following candidates.

        Job Title: Software Engineer
        Country: USA
        Company Size: 5000

        Job Title: Product Manager
        Company Size: 500

!!! warning "`expected`"

    &nbsp;The model must generate a Python function containing the specified conditional logic and arithmetic. The function should also gracefully handle cases where keys might be missing. It should then immediately discover and call this new function twice with the provided details in the form of a dictionary to return the calculated scores.
