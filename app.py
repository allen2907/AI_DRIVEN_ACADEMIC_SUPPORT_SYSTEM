from flask import Flask, render_template, request
import os
import re
import random
from PyPDF2 import PdfReader

app = Flask(__name__)

timetable = []
uploaded_file = None
syllabus_text = ""


# ==========================================================
# HOME / LOGIN
# ==========================================================

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    return redirect_to_dashboard()


def redirect_to_dashboard():
    files = get_uploaded_files()

    return render_template(
        "dashboard.html",
        uploaded_files=files,
        uploaded_file=uploaded_file
    )


# ==========================================================
# GET UPLOADED FILES
# ==========================================================

def get_uploaded_files():

    if not os.path.exists("uploads"):
        return []

    files = []

    for filename in os.listdir("uploads"):

        if filename.lower().endswith((".pdf", ".txt")):
            files.append(filename)

    files.sort()

    return files


# ==========================================================
# EXTRACT TEXT FROM FILE
# ==========================================================

def extract_file_text(filename):

    filepath = os.path.join("uploads", filename)

    if not os.path.exists(filepath):
        return ""

    try:

        if filename.lower().endswith(".pdf"):

            reader = PdfReader(filepath)

            text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return text

        elif filename.lower().endswith(".txt"):

            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

    except Exception:

        return ""

    return ""


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    return redirect_to_dashboard()


# ==========================================================
# UPLOAD SYLLABUS
# ==========================================================

@app.route("/upload", methods=["POST"])
def upload():

    global uploaded_file
    global syllabus_text

    file = request.files.get("syllabus")

    if not file or file.filename == "":

        return render_template(
            "dashboard.html",
            message="Please select a file.",
            uploaded_files=get_uploaded_files()
        )

    filename = file.filename

    os.makedirs("uploads", exist_ok=True)

    filepath = os.path.join("uploads", filename)

    file.save(filepath)

    uploaded_file = filename

    syllabus_text = extract_file_text(filename)

    return render_template(
        "dashboard.html",
        message="Syllabus uploaded successfully!",
        uploaded_files=get_uploaded_files(),
        uploaded_file=uploaded_file
    )


# ==========================================================
# VIEW SELECTED SYLLABUS
# ==========================================================

@app.route("/syllabus")
def syllabus():

    global uploaded_file
    global syllabus_text

    filename = request.args.get("filename")

    if filename:

        selected_text = extract_file_text(filename)

        if selected_text:

            uploaded_file = filename
            syllabus_text = selected_text

            return render_template(
                "syllabus.html",
                filename=filename,
                text=selected_text
            )

    if not syllabus_text:

        return render_template(
            "syllabus.html",
            message="No syllabus has been uploaded yet."
        )

    return render_template(
        "syllabus.html",
        filename=uploaded_file,
        text=syllabus_text
    )


# ==========================================================
# AI NOTES
# ==========================================================

@app.route("/generate_notes", methods=["POST"])
def generate_notes():

    global uploaded_file
    global syllabus_text

    filename = request.form.get("filename")

    if not filename:

        return render_template(
            "notes.html",
            message="Please select a study material first."
        )

    selected_text = extract_file_text(filename)

    if not selected_text:

        return render_template(
            "notes.html",
            message="Unable to read the selected study material."
        )

    uploaded_file = filename
    syllabus_text = selected_text

    text = selected_text.strip()

    # ------------------------------------------------------
    # SPLIT INTO SENTENCES
    # ------------------------------------------------------

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 25
    ]

    # ------------------------------------------------------
    # QUICK SUMMARY
    # ------------------------------------------------------

    summary = sentences[:5]

    # ------------------------------------------------------
    # IMPORTANT POINTS
    # ------------------------------------------------------

    important_words = [

        "algorithm",
        "complexity",
        "binary search",
        "sorting",
        "machine learning",
        "classification",
        "regression",
        "database",
        "sql",
        "normalization",
        "operating system",
        "process",
        "thread",
        "inheritance",
        "exception",
        "python",
        "java",
        "data structure",
        "graph",
        "tree",
        "knn",
        "decision tree",
        "random forest"
    ]

    key_points = []

    for sentence in sentences:

        sentence_lower = sentence.lower()

        for word in important_words:

            if word in sentence_lower:

                if sentence not in key_points:
                    key_points.append(sentence)

                break

        if len(key_points) >= 10:
            break

    if len(key_points) < 5:

        for sentence in sentences:

            if sentence not in key_points:
                key_points.append(sentence)

            if len(key_points) >= 10:
                break

    # ------------------------------------------------------
    # KEYWORDS
    # ------------------------------------------------------

    words = re.findall(
        r'\b[A-Za-z]{4,}\b',
        text.lower()
    )

    stop_words = {

        "about",
        "which",
        "these",
        "those",
        "their",
        "there",
        "where",
        "using",
        "between",
        "through",
        "should",
        "would",
        "could",
        "other",
        "being",
        "having",
        "because",
        "student",
        "students",
        "course",
        "subject",
        "unit",
        "lecture",
        "notes",
        "engineering",
        "introduction",
        "chapter"
    }

    word_frequency = {}

    for word in words:

        if word not in stop_words:

            word_frequency[word] = (
                word_frequency.get(word, 0) + 1
            )

    sorted_words = sorted(
        word_frequency,
        key=word_frequency.get,
        reverse=True
    )

    keywords = sorted_words[:15]

    # ------------------------------------------------------
    # DETECT TOPICS
    # ------------------------------------------------------

    topic_list = [

        "Algorithms",
        "Algorithm Analysis",
        "Time Complexity",
        "Space Complexity",
        "Binary Search",
        "Sorting",
        "Data Structures",
        "Machine Learning",
        "Supervised Learning",
        "Unsupervised Learning",
        "Classification",
        "Regression",
        "KNN",
        "Decision Tree",
        "Random Forest",
        "Database",
        "SQL",
        "Normalization",
        "Operating Systems",
        "Processes",
        "Threads",
        "Java",
        "Inheritance",
        "Exception Handling",
        "Python",
        "Graphs",
        "Trees"
    ]

    detected_topics = []

    text_lower = text.lower()

    for topic in topic_list:

        if topic.lower() in text_lower:

            detected_topics.append(topic)

    # ------------------------------------------------------
    # EXAM FOCUS
    # ------------------------------------------------------

    exam_focus = []

    exam_keywords = [

        "definition",
        "algorithm",
        "complexity",
        "advantages",
        "disadvantages",
        "applications",
        "types",
        "classification",
        "comparison",
        "architecture",
        "implementation"
    ]

    for sentence in sentences:

        sentence_lower = sentence.lower()

        for word in exam_keywords:

            if word in sentence_lower:

                if sentence not in exam_focus:
                    exam_focus.append(sentence)

                break

        if len(exam_focus) >= 6:
            break

    return render_template(
        "notes.html",
        filename=filename,
        summary=summary,
        key_points=key_points,
        keywords=keywords,
        topics=detected_topics,
        exam_focus=exam_focus
    )


# ==========================================================
# QUESTION BANK
# ==========================================================

QUESTION_BANK = {

    "algorithm": [

        {
            "question": "What is an algorithm?",
            "options": [
                "A finite sequence of well-defined steps used to solve a problem",
                "A physical component of a computer",
                "A type of database table",
                "A programming language"
            ],
            "answer": "A finite sequence of well-defined steps used to solve a problem"
        },

        {
            "question": "Which property of an algorithm means that it must eventually terminate?",
            "options": [
                "Finiteness",
                "Input",
                "Output",
                "Recursion"
            ],
            "answer": "Finiteness"
        },

        {
            "question": "What is the purpose of analyzing an algorithm?",
            "options": [
                "To determine its efficiency in terms of time and space",
                "To change the computer hardware",
                "To create a database",
                "To design a web page"
            ],
            "answer": "To determine its efficiency in terms of time and space"
        },

        {
            "question": "Which of the following is an important characteristic of a good algorithm?",
            "options": [
                "It should provide a clear and finite sequence of steps",
                "It should contain unlimited steps",
                "It should depend only on hardware",
                "It should never produce an output"
            ],
            "answer": "It should provide a clear and finite sequence of steps"
        }
    ],

    "algorithms": [

        {
            "question": "Which notation is commonly used to represent the upper bound of an algorithm's growth rate?",
            "options": [
                "Big O notation",
                "HTML notation",
                "SQL notation",
                "Binary notation"
            ],
            "answer": "Big O notation"
        },

        {
            "question": "Which of the following is used to compare algorithm efficiency?",
            "options": [
                "Time and space complexity",
                "Screen resolution",
                "File extension",
                "Keyboard layout"
            ],
            "answer": "Time and space complexity"
        }
    ],

    "design and analysis": [

        {
            "question": "What is the main purpose of algorithm design and analysis?",
            "options": [
                "To develop correct and efficient solutions to computational problems",
                "To manufacture computer processors",
                "To design computer networks only",
                "To create graphical interfaces only"
            ],
            "answer": "To develop correct and efficient solutions to computational problems"
        },

        {
            "question": "Which factor is commonly considered when analyzing an algorithm?",
            "options": [
                "Time complexity",
                "Monitor size",
                "Keyboard type",
                "Printer speed"
            ],
            "answer": "Time complexity"
        }
    ],

    "complexity": [

        {
            "question": "What does time complexity describe?",
            "options": [
                "How the running time of an algorithm grows with input size",
                "The physical size of a computer",
                "The amount of storage on a hard disk",
                "The speed of an internet connection"
            ],
            "answer": "How the running time of an algorithm grows with input size"
        },

        {
            "question": "Which complexity generally grows more slowly for large input sizes?",
            "options": [
                "O(log n)",
                "O(n²)",
                "O(n³)",
                "O(2ⁿ)"
            ],
            "answer": "O(log n)"
        },

        {
            "question": "What does space complexity measure?",
            "options": [
                "The amount of memory required by an algorithm",
                "The running time of a program",
                "The size of a computer screen",
                "The number of users on a network"
            ],
            "answer": "The amount of memory required by an algorithm"
        }
    ],

    "binary search": [

        {
            "question": "What condition is required for binary search to work correctly?",
            "options": [
                "The data must be sorted",
                "The data must contain only strings",
                "The data must contain no duplicates",
                "The data must be stored in a database"
            ],
            "answer": "The data must be sorted"
        },

        {
            "question": "What is the time complexity of binary search in the average case?",
            "options": [
                "O(log n)",
                "O(n)",
                "O(n²)",
                "O(2ⁿ)"
            ],
            "answer": "O(log n)"
        },

        {
            "question": "What does binary search do at each step?",
            "options": [
                "It divides the search space into two parts",
                "It checks every element from the beginning",
                "It deletes half of the array",
                "It sorts the entire array"
            ],
            "answer": "It divides the search space into two parts"
        }
    ],

    "linear search": [

        {
            "question": "How does linear search generally find an element?",
            "options": [
                "By checking elements one by one",
                "By repeatedly dividing the search space in half",
                "By sorting the array first",
                "By using a binary tree only"
            ],
            "answer": "By checking elements one by one"
        },

        {
            "question": "What is the worst-case time complexity of linear search?",
            "options": [
                "O(n)",
                "O(log n)",
                "O(1)",
                "O(n²)"
            ],
            "answer": "O(n)"
        }
    ],

    "sorting": [

        {
            "question": "What is the main purpose of a sorting algorithm?",
            "options": [
                "To arrange data in a specified order",
                "To delete all data",
                "To encrypt a file",
                "To create a database"
            ],
            "answer": "To arrange data in a specified order"
        },

        {
            "question": "Which of the following is a sorting algorithm?",
            "options": [
                "Merge Sort",
                "Binary Search",
                "Breadth First Search",
                "Depth First Search"
            ],
            "answer": "Merge Sort"
        },

        {
            "question": "What is the typical time complexity of Merge Sort?",
            "options": [
                "O(n log n)",
                "O(n²)",
                "O(log n)",
                "O(2ⁿ)"
            ],
            "answer": "O(n log n)"
        }
    ],

    "data structure": [

        {
            "question": "What is a data structure?",
            "options": [
                "A way of organizing and storing data for efficient access and modification",
                "A computer operating system",
                "A programming language",
                "A network protocol"
            ],
            "answer": "A way of organizing and storing data for efficient access and modification"
        }
    ],

    "stack": [

        {
            "question": "Which principle does a stack follow?",
            "options": [
                "LIFO (Last In, First Out)",
                "FIFO (First In, First Out)",
                "Random access only",
                "Priority based access"
            ],
            "answer": "LIFO (Last In, First Out)"
        },

        {
            "question": "Which operation adds an element to a stack?",
            "options": [
                "Push",
                "Pop",
                "Delete",
                "Search"
            ],
            "answer": "Push"
        }
    ],

    "queue": [

        {
            "question": "Which principle does a queue normally follow?",
            "options": [
                "FIFO (First In, First Out)",
                "LIFO (Last In, First Out)",
                "Random access",
                "Reverse order only"
            ],
            "answer": "FIFO (First In, First Out)"
        },

        {
            "question": "Which operation removes an element from the front of a queue?",
            "options": [
                "Dequeue",
                "Enqueue",
                "Push",
                "Insert"
            ],
            "answer": "Dequeue"
        }
    ],

    "machine learning": [

        {
            "question": "What is Machine Learning?",
            "options": [
                "A field where computers learn patterns from data to make predictions or decisions",
                "A method of physically repairing computers",
                "A type of computer network",
                "A database storage technique"
            ],
            "answer": "A field where computers learn patterns from data to make predictions or decisions"
        },

        {
            "question": "Which is an example of supervised learning?",
            "options": [
                "Classification using labelled training data",
                "Grouping customers without labels",
                "Reducing file size",
                "Managing computer memory"
            ],
            "answer": "Classification using labelled training data"
        }
    ],

    "knn": [

        {
            "question": "What does KNN stand for?",
            "options": [
                "K-Nearest Neighbors",
                "Known Neural Network",
                "Kernel Node Network",
                "Key Nearest Number"
            ],
            "answer": "K-Nearest Neighbors"
        },

        {
            "question": "How does KNN make a prediction?",
            "options": [
                "By considering the nearest training examples",
                "By randomly selecting an answer",
                "By sorting a database alphabetically",
                "By removing all training data"
            ],
            "answer": "By considering the nearest training examples"
        }
    ],

    "decision tree": [

        {
            "question": "What is a Decision Tree mainly used for?",
            "options": [
                "Classification and regression",
                "Only file compression",
                "Only network routing",
                "Only image storage"
            ],
            "answer": "Classification and regression"
        }
    ],

    "random forest": [

        {
            "question": "What is a Random Forest?",
            "options": [
                "An ensemble of multiple decision trees",
                "A single linear regression model",
                "A database management system",
                "A computer network protocol"
            ],
            "answer": "An ensemble of multiple decision trees"
        }
    ],

    "database": [

        {
            "question": "What is the main purpose of a database?",
            "options": [
                "To store and manage organized data",
                "To increase monitor brightness",
                "To compile Java programs",
                "To connect a keyboard"
            ],
            "answer": "To store and manage organized data"
        }
    ],

    "sql": [

        {
            "question": "What does SQL stand for?",
            "options": [
                "Structured Query Language",
                "Simple Question Language",
                "System Query Logic",
                "Structured Queue Language"
            ],
            "answer": "Structured Query Language"
        },

        {
            "question": "Which SQL command is used to retrieve data?",
            "options": [
                "SELECT",
                "DELETE",
                "DROP",
                "INSERT"
            ],
            "answer": "SELECT"
        }
    ],

    "normalization": [

        {
            "question": "What is the main purpose of database normalization?",
            "options": [
                "To reduce data redundancy and improve data integrity",
                "To increase duplicate data",
                "To delete all tables",
                "To increase network speed"
            ],
            "answer": "To reduce data redundancy and improve data integrity"
        }
    ],

    "operating system": [

        {
            "question": "What is an operating system?",
            "options": [
                "System software that manages computer hardware and software resources",
                "A database table",
                "A programming language",
                "A web browser"
            ],
            "answer": "System software that manages computer hardware and software resources"
        }
    ],

    "python": [

        {
            "question": "Which symbol is used to start a comment in Python?",
            "options": [
                "#",
                "//",
                "/*",
                "<!--"
            ],
            "answer": "#"
        }
    ],

    "java": [

        {
            "question": "Which concept allows a Java class to acquire properties and methods from another class?",
            "options": [
                "Inheritance",
                "Compilation",
                "Encapsulation only",
                "Exception handling"
            ],
            "answer": "Inheritance"
        }
    ]
}


# ==========================================================
# GENERATE QUESTIONS
# ==========================================================

def generate_questions(text):

    text_lower = text.lower()

    matched_questions = []

    topics = sorted(
        QUESTION_BANK.keys(),
        key=len,
        reverse=True
    )

    for topic in topics:

        if topic in text_lower:

            for question in QUESTION_BANK[topic]:

                if question not in matched_questions:

                    matched_questions.append(question)

    random.shuffle(matched_questions)

    return matched_questions[:10]


# ==========================================================
# AI TEST
# ==========================================================

@app.route("/generate_test")
def generate_test():

    if not syllabus_text:

        return render_template(
            "test.html",
            message="Please upload a syllabus first."
        )

    questions = generate_questions(
        syllabus_text
    )

    if not questions:

        questions = [

            {
                "question": "Which activity is an important part of academic learning?",
                "options": [
                    "Understanding concepts and practicing questions",
                    "Ignoring the study material",
                    "Avoiding revision",
                    "Skipping all practice"
                ],
                "answer": "Understanding concepts and practicing questions"
            },

            {
                "question": "Why is it useful to analyze study material?",
                "options": [
                    "To identify important concepts and understand the subject",
                    "To delete the study material",
                    "To avoid learning",
                    "To replace the syllabus"
                ],
                "answer": "To identify important concepts and understand the subject"
            }
        ]

    return render_template(
        "test.html",
        filename=uploaded_file,
        questions=questions
    )


# ==========================================================
# SUBMIT TEST
# ==========================================================

@app.route("/submit_test", methods=["POST"])
def submit_test():

    score = 0
    total = 0

    for key in request.form:

        if key.startswith("answer_"):

            index = key.split("_")[1]

            user_answer = request.form.get(key)

            correct_answer = request.form.get(
                "correct_" + index
            )

            total += 1

            if user_answer == correct_answer:
                score += 1

    percentage = 0

    if total > 0:

        percentage = round(
            (score / total) * 100,
            2
        )

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage
    )


# ==========================================================
# QUICK QUIZ
# ==========================================================

@app.route("/quiz")
def quiz():

    questions = [

        {
            "question": "What does ML stand for?",
            "options": [
                "Machine Learning",
                "Manual Logic",
                "Machine Language",
                "Memory Learning"
            ],
            "answer": "Machine Learning"
        },

        {
            "question": "Which language is commonly used for Machine Learning?",
            "options": [
                "Python",
                "HTML",
                "CSS",
                "XML"
            ],
            "answer": "Python"
        },

        {
            "question": "Which algorithm can be used for classification?",
            "options": [
                "Decision Tree",
                "HTML",
                "CSS",
                "SQL"
            ],
            "answer": "Decision Tree"
        }
    ]

    return render_template(
        "test.html",
        filename="Quick Academic Quiz",
        questions=questions
    )


# ==========================================================
# TIMETABLE
# ==========================================================

@app.route("/timetable")
def timetable_page():

    return render_template(
        "timetable.html",
        timetable=timetable
    )


@app.route("/add_timetable", methods=["POST"])
def add_timetable():

    subject = request.form.get("subject")
    day = request.form.get("day")
    time = request.form.get("time")

    if subject and day and time:

        timetable.append({
            "subject": subject,
            "day": day,
            "time": time
        })

    return render_template(
        "timetable.html",
        timetable=timetable
    )


# ==========================================================
# LEARNING RESOURCES
# ==========================================================

@app.route("/resources")
def resources():

    return render_template(
        "resources.html"
    )


# ==========================================================
# PREVIOUS YEAR QUESTIONS
# ==========================================================

@app.route("/pyq")
def pyq():

    return render_template(
        "pyq.html"
    )


# ==========================================================
# AI TOOLS
# ==========================================================

@app.route("/ai_tools")
def ai_tools():

    return render_template(
        "ai_tools.html"
    )


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    print("================================")
    print("AI STUDENT ASSISTANT STARTED")
    print("================================")

    app.run(debug=True)