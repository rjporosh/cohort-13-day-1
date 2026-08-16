namespace HospitalDoctorPatient.Domain;

public class Appointment
{
    public DateTime Date { get; }

    public Appointment(DateTime date)
    {
        if (date < DateTime.Now)
            throw new ArgumentException(
                "Appointment cannot be in the past.");

        Date = date;
    }
}