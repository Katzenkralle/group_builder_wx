Reports and Notes from the Author
----------------------------------

Controlflow Diagram of the Algorithm:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. image:: algorythmControlFlow.png
   :align: center
   :alt: Main Frame


Testing and Quality Assurance:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Due to the intended use case of the application and the nature of the group finder algorithm,  
it was decided that concrete unit tests are not critical for the application.  
This decision allowed time and resources to be allocated toward improving the overall user experience,  
e.g., by adding non-modal dialogs and info boxes during the group generation process.

To compensate for the lack of unit tests, the application was tested by a group of five people,  
who identified and helped fix the following bugs:

- The alias editor failed to block the dropdown **"Iteration Selection"** in CSV import mode.
- Canceling the group generation process did not always stop execution.
- The **"Invalid group composition"** message box failed to display.
- etc.
