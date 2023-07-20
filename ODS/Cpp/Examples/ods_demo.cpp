#include <iostream>
#include <fstream>
#include <chrono>
#include <thread>
#include <cstdint>

#include "ods_config.h"
#include "ods_get_data.h"
#include "diagnostic.h"
#define JSON_USE_GLOBAL_UDLS 0
#include <nlohmann/json.hpp>

#include <ifm3d/device/o3r.h>
using namespace ifm3d::literals;

int main()
{
    ////////////////////////////////////////////////
    // Define the variables used in the example
    ////////////////////////////////////////////////
    // O3R and ODS configuration
    // Getting IP from environment variable
    const char* IP = std::getenv("IFM3D_IP");
    if (!IP) {
        IP = ifm3d::DEFAULT_IP.c_str();
        std::clog << "Using default IP" << std::endl;        
    }
    std::clog << "IP: " << IP << std::endl;

    ifm3d::FrameGrabber::BufferList buffer_list = {ifm3d::buffer_id::O3R_ODS_INFO, ifm3d::buffer_id::O3R_ODS_OCCUPANCY_GRID};
    std::string forward_app = "app0";
    std::string backward_app = "app1";
    int timeout_ms = 500; // Timeout used when retrieving data
    // Config file for extrinsic calibrations and apps
    std::string config_extrinsic_path = "../Configs/extrinsic_two_heads.json";
    std::string config_app_path = "../Configs/ods_two_apps_config.json";
    // Data display configuration
    int step = 5;         // Used to reduce the frequency of the data displayed
    int d = 5;            // How long data will be displayed for each app
    // Logging configuration
    bool log_to_file = true;
    const std::string& log_file_name = "ODS_logfile.txt";
    
    std::ofstream logFile;
    std::streambuf* consoleBuffer = std::clog.rdbuf();
    std::clog.rdbuf(consoleBuffer);
    if (log_to_file)
    {
        logFile.open(log_file_name, std::ios::app);  // Open the log file
        // Check if the file opened successfully
        if (!logFile.is_open())
        {
            std::cerr << "Failed to open log file: " << log_file_name << std::endl;
            return 1;  // Return an error code or handle the error appropriately
        }

        std::streambuf* fileBuffer = logFile.rdbuf();
        // Redirect std::clog to the log file
        std::clog.rdbuf(fileBuffer);
    }

    auto o3r = std::make_shared<ifm3d::O3R>(IP);

    // TODO: bootup monitoring

    ////////////////////////////////////////////////
    // Check the diagnostic for any active errors.
    ////////////////////////////////////////////////
    O3RDiagnostic diagnostic(o3r);
    ifm3d::json::json_pointer p("/events");
    ifm3d::json active_diag = diagnostic.GetDiagnosticFiltered(ifm3d::json::parse(R"({"state":"active"})"))[p];

    for (auto error = active_diag.begin(); error != active_diag.end(); ++error)
    {
        std::clog << "\n//////////////////////////////////" << std::endl;
        std::clog << *error << std::endl;
    }
    std::clog << "Review any active errors before continuing" << std::endl;

    do
    {
        std::clog << '\n' << "Press \"ENTER\" when ready to continue...";
    } while (std::cin.get() != '\n');

    std::clog << "Continuing with the tutorial" << std::endl;

    ////////////////////////////////////////////////
    // Start the asynchronous diagnostic
    ////////////////////////////////////////////////
    diagnostic.StartAsyncDiag();

    ////////////////////////////////////////////////
    // Configure two applications (forward and back)
    ////////////////////////////////////////////////
    ODSConfig ods_config(o3r);

    ods_config.SetConfigFromFile(config_extrinsic_path);
    // In FW <= 1.1.x, setting configurations is non-blocking.
    // We add a sleep command to ensure the call has
    // enought time to terminate.
    std::this_thread::sleep_for(std::chrono::seconds(1));
    ods_config.SetConfigFromFile(config_app_path);
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Verifying the proper instantiation of the two apps
    std::string j_string = "/applications/instances";
    ifm3d::json::json_pointer j(j_string);
    auto apps = o3r->Get({j_string})[j];

    for (auto app = apps.begin(); app != apps.end(); ++app)
    {
        std::clog << "Instantiated app: " << app.key() << std::endl;
    }
        
    ////////////////////////////////////////////////
    // Start streaming data from forward app (app0)
    ////////////////////////////////////////////////
    // Set the app to "RUN" state
    ods_config.SetConfigFromStr(R"({"applications": {"instances": {"app0": {"state": "RUN"}}}})");
    // Ensure that the configuration has time to terminate
    std::this_thread::sleep_for(std::chrono::seconds(1));

    ODSStream ods_stream0(o3r, forward_app, buffer_list, timeout_ms);
    ods_stream0.StartODSStream();
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Print out every 5th dataset until stopped
    int count = 0;
    for (auto start = std::chrono::steady_clock::now(), now = start; now < start + std::chrono::seconds{d}; now = std::chrono::steady_clock::now())
    {
        auto zones = ods_stream0.GetZones();
        auto grid = ods_stream0.GetOccGrid();

        if (count % step == 0)
        {
            std::clog << "Current zone occupancy:\n"
                      << std::to_string(zones.zone_occupied[0]) << ", "
                      << std::to_string(zones.zone_occupied[1]) << ", "
                      << std::to_string(zones.zone_occupied[2])
                      << std::endl;
            std::clog << "Current occupancy grid's middle cell:\n"
                      << std::to_string(grid.image.at<uint8_t>(100, 100))
                      << std::endl;
        }
        count++;
    }

    ods_stream0.StopODSStream();
    // Set the app to "CONF" to save energy
    ods_config.SetConfigFromStr(R"({"applications": {"instances": {"app0": {"state": "CONF"}}}})");
    std::this_thread::sleep_for(std::chrono::seconds(1));

    ////////////////////////////////////////////////
    // Start streaming data from backward app (app1)
    ////////////////////////////////////////////////    
    // Set the app to "RUN" state
    ods_config.SetConfigFromStr(R"({"applications": {"instances": {"app1": {"state": "RUN"}}}})");
    std::this_thread::sleep_for(std::chrono::seconds(1));

    ODSStream ods_stream1(o3r, backward_app, buffer_list, timeout_ms);
    ods_stream1.StartODSStream();
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Print out every 5th dataset until stopped
    count = 0;
    for (auto start = std::chrono::steady_clock::now(), now = start; now < start + std::chrono::seconds{d}; now = std::chrono::steady_clock::now())
    {
        auto zones = ods_stream1.GetZones();
        auto grid = ods_stream1.GetOccGrid();

        if (count % step == 0)
        {
            std::clog << "Current zone occupancy:\n"
                      << std::to_string(zones.zone_occupied[0]) << ", "
                      << std::to_string(zones.zone_occupied[1]) << ", "
                      << std::to_string(zones.zone_occupied[2])
                      << std::endl;
            std::clog << "Current occupancy grid's middle cell:\n"
                      << std::to_string(grid.image.at<uint8_t>(100, 100))
                      << std::endl;
        }
        count++;
    }

    ods_stream1.StopODSStream();
    // Set the app to "CONF" to save energy
    ods_config.SetConfigFromStr(R"({"applications": {"instances": {"app0": {"state": "CONF"}}}})");

    // Stop streaming diagnostic data and exit
    diagnostic.StopAsyncDiag();

    // Close the log file
    if (log_to_file)
    {
        logFile.close();
    }

    return 0;
}
