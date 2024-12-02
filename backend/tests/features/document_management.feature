Feature: Document Management and Search

  Scenario: User uploads a single document
    Given the system is ready for document upload
    When the user uploads a document "sample.pdf"
    Then the document should be successfully processed and indexed

  Scenario: User uploads multiple documents
    Given the system is ready for document upload
    When the user uploads documents "doc1.pdf" and "doc2.txt"
    Then all documents should be successfully processed and indexed

  Scenario: User processes a document
    Given a document "sample.pdf" is uploaded
    When the user initiates document processing
    Then the document should be processed and key phrases extracted

  Scenario: User deletes a document
    Given a document "sample.pdf" is indexed
    When the user deletes the document "sample.pdf"
    Then the document should be removed from the index

  Scenario: User deletes multiple documents
    Given documents "doc1.pdf" and "doc2.txt" are indexed
    When the user deletes documents "doc1.pdf" and "doc2.txt"
    Then the documents should be removed from the index

  Scenario: User performs a vector search
    Given the index contains processed documents
    When the user performs a vector search with query "AI technologies"
    Then the system should return relevant results
    And the LLM should generate a response based on the search results

  Scenario: User performs a hybrid search
    Given the index contains processed documents
    When the user performs a hybrid search with query "machine learning applications"
    Then the system should return relevant results
    And the LLM should generate a response based on the search results