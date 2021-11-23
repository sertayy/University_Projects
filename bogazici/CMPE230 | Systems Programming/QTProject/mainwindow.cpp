#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QDebug>
#include <QRegularExpression>

#define INTERVAL 1500

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    labels = new QLabel*[2];
    QString pair_name = "pairs_val";
    QString found_name = "found_val";
    labels[0] = MainWindow::findChild<QLabel*>(pair_name);
    labels[1] = MainWindow::findChild<QLabel*>(found_name);
    prevButton = new QPushButton;
    mButtons = new QPushButton*[ROWS*COLS];
    mStrings = new QString[ROWS*COLS];
    selected = nullptr;
    isSecondItemSelected = false;
    pairsTried = 0; pairsFound = 0;

    timer = new QTimer(this);
    timer->setSingleShot(true);
    connect(timer, SIGNAL(timeout()), this, SLOT(timeoutOccured()));
    resetGame();
}

void MainWindow::buttonPressed() {
    QPushButton *button = (QPushButton *)sender();
    QRegularExpression reg("\\d+");
    QRegularExpressionMatch match = reg.match(button->objectName());
    int index = match.captured(0).toInt()-1; // objects numbered 1 to 24

    if(isSecondItemSelected || timer->isActive()) {
        return;
    }
    if(index == selectedIndex)
        return;

    // if there is no selected item
    if(selected == nullptr){
        button->setText(mStrings[index]);
        selectedIndex = index;
        selected = mStrings[index];
        prevButton = button;
        return;
    }

    // if there is a selected item and it matches the one selected earlier
    if(index != selectedIndex && QString::compare(selected, mStrings[index]) == 0) {
        button->setText(mStrings[selectedIndex]);
        foundIndices.insert(index);
        foundIndices.insert(selectedIndex);
        disableButtons(button,prevButton);
        selected = nullptr;
        prevButton = nullptr;
        selectedIndex = -1;
        isSecondItemSelected = false;
        pairsFound++;
        pairsTried++;
        labels[1]->setText(QString::number(pairsFound));
        labels[0]->setText(QString::number(pairsTried));
        timer->start(INTERVAL);
        return;
    }
    // if there are two selected items but not more
    // this makes sure not more than 2 items gets selected
    if(!isSecondItemSelected && prevButton != nullptr){
        button->setText(mStrings[index]);
        isSecondItemSelected = true;
        pairsTried++;
        labels[0]->setText(QString::number(pairsTried));
        timer->start(INTERVAL);
    }
}
void MainWindow::changeColor(QColor color, QPushButton* button) {
    QPalette pal = button->palette();
    pal.setColor(QPalette::Button,color);
    button->setAutoFillBackground(true);
    button->setPalette(pal);
    button->update();
    return;
}
void MainWindow::disableButtons(QPushButton* button1, QPushButton* button2) {
    changeColor(Qt::black,button1);
    changeColor(Qt::black,button2);
    button1->setDisabled(true);
    button2->setDisabled(true);
    return;
}
void MainWindow::timeoutOccured() {
    isSecondItemSelected = false;
    selected = nullptr;
    prevButton = nullptr;
    selectedIndex = -1;
    hideButtonTexts();
    timer->stop();
}

void MainWindow::findButtons() {
    // get a handle for each button
    for(int i = 0; i < ROWS*COLS; i++){
        QString buttonName = "pushButton_" + QString::number(i+1);
        mButtons[i] = MainWindow::findChild<QPushButton*>(buttonName);
        connect(mButtons[i], SIGNAL(released()), this, SLOT(buttonPressed()));
    }
}

void MainWindow::resetGame() {
    findButtons();

    setRandomButtonTexts();
    pairsFound = 0;
    pairsTried = 0;
    labels[1]->setText(QString::number(0));
    labels[0]->setText(QString::number(0));
    selected = nullptr;
    selectedIndex = -1;
    isSecondItemSelected = false;
    foundIndices.clear();
    for(int i = 0; i < ROWS*COLS; i++) {
        mButtons[i]->setVisible(true);
        mButtons[i]->setDisabled(false);
    }
    timer->start(INTERVAL);
}

void MainWindow::setRandomButtonTexts() {
    QSet<char> usedChars;
    QSet<int> usedIndices;
    // reset the buttons with random chars
    for(int i = 0; i < ROWS*COLS*0.5; i++) {
        // get a unique char
        char c = 'a';
        do {
            c = static_cast<char>(QRandomGenerator::global()->bounded('A', 'Z'+1));
        }while(usedChars.contains(c));
        usedChars.insert(c);
        mButtons[i]->setText(QString(c));
        changeColor(Qt::red,mButtons[i]);//assign color
        mStrings[i] = QString(c);

        // get a unique pair
        int pairIndex = 0;
        do {
            pairIndex = static_cast<int>(QRandomGenerator::global()->bounded(ROWS*COLS/2, ROWS*COLS));
        }while(usedIndices.contains(pairIndex));
        usedIndices.insert(pairIndex);
        mButtons[pairIndex]->setText(QString(c));
        changeColor(Qt::red,mButtons[pairIndex]);
        mStrings[pairIndex] = QString(c);
    }
}

void MainWindow::hideButtonTexts() {
    assert(mButtons != nullptr);
    for(int i = 0; i < ROWS*COLS; i++) {
        if(!foundIndices.contains(i))
            mButtons[i]->setText("");
    }
}

void MainWindow::revealButtonTexts() {
    assert(mButtons != nullptr);
    for(int i = 0; i < ROWS*COLS; i++) {
        mButtons[i]->setText(mStrings[i]);
    }
}

void MainWindow::on_Reset_released()
{
    resetGame();
}

MainWindow::~MainWindow()
{
    delete ui;
}
