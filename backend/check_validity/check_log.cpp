//Hata mig inte, inte jag som har skrivit denna koden, enbart python filen. Denna är mer ett test!

#include <iostream>
#include <fstream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <logfile> <search_term>" << std::endl;
        return 1;
    }

    std::string logfile = argv[1];
    std::string search_term = argv[2];

    std::ifstream file(logfile);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << logfile << std::endl;
        return 1;
    }

    std::string line;
    bool found = false;
    while (std::getline(file, line)) {
        if (line.find(search_term) != std::string::npos) {
            found = true;
            break;
        }
    }

    file.close();

    if (found) {
        std::cout << "Found: " << search_term << " in " << logfile << std::endl;
        return 0;
    } else {
        std::cout << "Not Found: " << search_term << " in " << logfile << std::endl;
        return 1;
    }
}
